from datetime import datetime
import connexion
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler 
import requests
import json

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

STATS_FILE = "stats.json"
STORAGE_URL = "http://localhost:8090"  # storage service base URL

def populate_stats():
    logger.info("Periodic processing started")

    # --- Read existing stats or use defaults ---
    try:
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
    except FileNotFoundError:
        stats = {
            "temperature": {
                "num_temp_readings": 500000,
                "min_temp_celcius": -60,
                "max_temp_celcius": 60,
                "last_updated": "2025-01-01T00:00:00Z"
            },
            "motion": {
                "num_motion_readings": 250000,
                "min_animal_speed": 0,
                "max_animal_speed": 15,
                "last_updated": "2025-01-01T00:00:00Z"
            }
        }

    now = datetime.utcnow().isoformat() + "Z"

    # --- Fetch new temperature events ---
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

    # --- Fetch new motion events ---
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

    # --- Update temperature stats ---
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
        stats["temperature"]["last_updated"] = max([t["reading_timestamp"] for t in new_temps])

    # --- Update motion stats ---
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
        stats["motion"]["last_updated"] = max([m["recorded_timestamp"] for m in new_motion])

    # --- Save updated stats ---
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

    logger.debug(f"Updated statistics: {stats}")
    logger.info("Periodic processing ended")



def init_scheduler(interval_seconds=10):
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=interval_seconds)
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

if __name__ == "__main__":
    init_scheduler() 
    app.run(port=8100)
