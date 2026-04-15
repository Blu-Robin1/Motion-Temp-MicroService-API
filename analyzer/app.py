from flask_cors import CORS
import json
import connexion
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from connexion import NoContent
import yaml
import logging
import logging.config
from pykafka import KafkaClient 
from kafka_wrapper import KafkaWrapper

# app.py

def health_check():
    return {"status": "ok"}


# Configure logging FIRST
with open('../config/analyzer_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

# Load app config
with open('../config/analyzer_config.yml', 'r') as f:
    app_config = yaml.safe_load(f)

hostname=app_config['kafka']['hostname']
topic=app_config['kafka']['topic']

kafka_wrapper = KafkaWrapper(hostname, topic)

def get_temp_reading(index):
    logger.info("Get request for temperature_reading")

    messages = kafka_wrapper.consume_all_messages()
    counter = 0

    for msg in messages:
        data = json.loads(msg.value.decode("utf-8"))

        if data.get("type") == "temperature_report":
            if counter == index:
                logger.info("Sending temperature_reading")
                return data.get("payload", {}), 200
            counter += 1

    logger.info("Temperature reading not found")
    return {"message": f"No temperature event at index {index}!"}, 404

def get_motion_reading(index):
    logger.info("Get request for motion_reading")

    messages = kafka_wrapper.consume_all_messages()
    counter = 0

    for msg in messages:
        data = json.loads(msg.value.decode("utf-8"))

        if data.get("type") == "motion_report":
            if counter == index:
                logger.info("Sending motion_reading")
                return data.get("payload", {}), 200
            counter += 1

    logger.info("Motion reading not found")
    return {"message": f"No motion event at index {index}!"}, 404


def get_reading_stats():
    logger.info("Get request for stats")

    messages = kafka_wrapper.consume_all_messages()
    num_temp = 0
    num_motion = 0

    for msg in messages:
        data = json.loads(msg.value.decode("utf-8"))
        if data.get("type") == "temperature_report":
            num_temp += 1
        elif data.get("type") == "motion_report":
            num_motion += 1

    stats = {
        "num_temp_readings": num_temp,
        "num_motion_readings": num_motion
    }

    logger.info("Sending stats")
    return stats, 200

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app, origins="*")

app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

if __name__ == "__main__":
    app.run(port=8025, host="0.0.0.0")
