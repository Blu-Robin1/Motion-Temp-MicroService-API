import json
import connexion
from connexion import NoContent
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

    logger.info("Get request for temperature_reading")

    client = KafkaClient(hosts=app_config["kafka"]["hostname"])
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True,
        consumer_timeout_ms=1000
    )
        
    counter = 0

    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        payload = data.get("payload",{})

        if data.get("type") == "temperature_report":
            payload = data.get("payload", {})

            if counter == index:
                logger.info("Sending temperature_reading")
                return payload, 200

            counter += 1
    
    try:
        consumer.stop()
    except Exception:
        pass

    logger.info("Temperature reading not found")
    return {"message": f"No temperature event at index {index}!"}, 404


def get_motion_reading(index):

    logger.info(f"Get request for motion_reading")

    client = KafkaClient(hosts=app_config["kafka"]["hostname"])
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    counter = 0

    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        payload = data.get("payload",{})

        if data.get("type") == "motion_report":
            payload = data.get("payload", {})

            if counter == index:
                logger.info("Sending motion_reading")
                return payload, 200

            counter += 1
    
    try:
        consumer.stop()
    except Exception:
        pass

    logger.info("Motion reading not found")
    return {"message": f"No Motion event at index {index}!"}, 404



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
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

application = app.app

if __name__ == "__main__":
    app.run(port=8025, host="0.0.0.0")