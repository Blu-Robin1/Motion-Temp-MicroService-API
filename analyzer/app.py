import datetime
import json
import connexion
from connexion import NoContent
import httpx
import time
import yaml
import logging
import logging.config
from pykafka import KafkaClient 

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f)


def get_temp_reading(index):

    logger.info(f"Get request for temperature_reading")

    client = KafkaClient(hosts=app_config["kafka"]["hostname"])
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    counter = 0
    
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        # Look for the index requested and return the payload with 200 status code

        if index in data:
            return {"index_requested": data[index]}, 200

        counter+=1

    logger.info("Sending temperature_reading")

    return { "message": f"No event at index {index}!"}, 404


def get_motion_reading(index):

    logger.info(f"Get request for motion_reading")

    client = KafkaClient(hosts=app_config["kafka"]["hostname"])
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    counter = 0

    for msg in consumer:
        if counter == index:
            message = msg.value.decode("utf-8")
            data = json.loads(message)

            logger.info("Sending temperature_reading")
            return data, 200

        counter += 1

    return {"message": f"No event at index {index}!"}, 404



def get_reading_stats():

    logger.info("Get request for stats")

    client = KafkaClient(hosts=app_config["kafka"]["hostname"])
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True,
        consumer_timeout_ms=1000
    )

    num_temp = 0
    num_motion = 0

    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)

        if "temperature_celsius" in data:
            num_temp += 1
        elif "animal_speed" in data:
            num_motion += 1

    stats = {
        "num_temp_readings": num_temp,
        "num_motion_readings": num_motion
    }

    logger.info("Sending stats")
    return stats, 200


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

application = app.app

if __name__ == "__main__":
    app.run(port=8020)