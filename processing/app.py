from datetime import datetime
import connexion
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler 
import requests
import json
from flask import jsonify, make_response
from pathlib import Path
#from kafka_wrapper import KafkaWrapper
from flask_cors import CORS
import os

# app.py

def health_check():
    return {"status": "ok"}


# Configure logging FIRST
with open('../config/processing_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

# Load app config
with open('../config/processing_config.yml', 'r') as f:
    app_config = yaml.safe_load(f)

# THEN create Kafka wrapper
#kafka_wrapper = KafkaWrapper("kafka:9092", b"events")


INTRAVEL = app_config['scheduler']['interval']
STATS_FILE = app_config['stats_file_name']['name']
STORAGE_URL = app_config['storage_url']['url']

def get_stats():
    """GET endpoint for returning current statistics"""
    logger.info("Received request for current statistics")

    stats_path = Path(STATS_FILE)

    if not stats_path.exists():
        logger.error("Statistics file does not exist: %s", STATS_FILE)
        return make_response(
            jsonify({"message": "Statistics do not exist"}), 404
        )

    with stats_path.open("r") as f:
        stats = json.load(f)

    logger.debug("Statistics read from file: %s", stats)
    logger.info("Request for current statistics completed")

    return jsonify(stats), 200

def populate_stats():
    logger.info("Periodic processing started")

    try:
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
    except FileNotFoundError:
        stats = {
            "temperature": {
                "num_temp_readings": 0,
                "min_temp_celcius": None,
                "max_temp_celcius": None,
                "last_updated": "2025-01-01T00:00:00Z"
            },
            "motion": {
                "num_motion_readings": 0,
                "min_animal_speed": None,
                "max_animal_speed": None,
                "last_updated": "2025-01-01T00:00:00Z"
            }
        }

    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    
    temp_start = stats["temperature"]["last_updated"]
    temp_resp = requests.get(
        f"{STORAGE_URL}/motiontemp/temperature",
        params={"start_timestamp": temp_start, "end_timestamp": now}
    )

    if temp_resp.status_code != 200:
        logger.error(f"Temperature GET request failed with status {temp_resp.status_code}")
        new_temps = []
    else:
        new_temps = temp_resp.json()
        logger.info(f"Received {len(new_temps)} new temperature events")

    motion_start = stats["motion"]["last_updated"]
    motion_resp = requests.get(
        f"{STORAGE_URL}/motiontemp/motion",
        params={"start_timestamp": motion_start, "end_timestamp": now}
    )

    if motion_resp.status_code != 200:
        logger.error(f"Motion GET request failed with status {motion_resp.status_code}")
        new_motion = []
    else:
        new_motion = motion_resp.json()
        logger.info(f"Received {len(new_motion)} new motion events")

    temp_values = [t["temperature_celsius"] for t in new_temps]
    if temp_values:
        stats["temperature"]["num_temp_readings"] += len(temp_values)
        stats["temperature"]["min_temp_celcius"] = (
            min(temp_values) if stats["temperature"]["min_temp_celcius"] is None
            else min(stats["temperature"]["min_temp_celcius"], min(temp_values))
        )
        stats["temperature"]["max_temp_celcius"] = (
            max(temp_values) if stats["temperature"]["max_temp_celcius"] is None
            else max(stats["temperature"]["max_temp_celcius"], max(temp_values))
        )
        stats["temperature"]["last_updated"] = now
    speeds = [m["animal_speed"] for m in new_motion]
    if speeds:
        stats["motion"]["num_motion_readings"] += len(speeds)
        stats["motion"]["min_animal_speed"] = (
            min(speeds) if stats["motion"]["min_animal_speed"] is None
            else min(stats["motion"]["min_animal_speed"], min(speeds))
        )
        stats["motion"]["max_animal_speed"] = (
            max(speeds) if stats["motion"]["max_animal_speed"] is None
            else max(stats["motion"]["max_animal_speed"], max(speeds))
        )
        stats["motion"]["last_updated"] = now
        
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

    logger.debug(f"Updated statistics: {stats}")
    logger.info("Periodic processing ended")



def init_scheduler(INTRAVEL):
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=INTRAVEL)
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app, origins="*")

app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True,
    base_path="/processing"

)

if __name__ == "__main__":
    init_scheduler(INTRAVEL)
    app.run(port=8100, host="0.0.0.0")
