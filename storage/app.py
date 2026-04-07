from datetime import datetime
import json
from threading import Thread
import connexion
from connexion import NoContent
from db import make_session
from models import Temperature, Motion
import yaml
import logging
import logging.config
from sqlalchemy import select
from pykafka import KafkaClient
from pykafka.common import OffsetType 
from kafka_wrapper import KafkaWrapper

# Configure logging FIRST
with open('../config/storage_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

# Load app config
with open('../config/storage_config.yml', 'r') as f:
    app_config = yaml.safe_load(f)

hosts=app_config['events']['hostname']
port=app_config['events']['port']
topic=app_config['events']['topic']

kafka_wrapper = KafkaWrapper(
    f"{hosts}:{port}",
    topic.encode("utf-8")
)


#logger = logging.getLogger('basicLogger')

def report_temperature_readings(body):
    """Receives a temperature batch event and stores events in DB"""
    session = make_session()
    logger.info(f"Received event temperature_report with a trace id of {body.get("trace_id")}")

    event = Temperature(
        station_id=body["station_id"],
        station_name=body["station_name"],
        temperature_celsius=body["temperature_celsius"],
        reporting_timestamp=datetime.fromisoformat(
            body["reporting_timestamp"].replace("Z", "+00:00")
        ),
        recorded_timestamp=datetime.fromisoformat(
            body["recorded_timestamp"].replace("Z", "+00:00")
        ),
        trace_id=body.get("trace_id")  
    )
    session.add(event)
    session.commit()
    session.close()
    
    logger.debug("Stored event temperature_report with a trace id of %s",body["trace_id"])

def report_motion_readings(body):
    """Receives a motion detection event and stores it in DB"""
    session = make_session()
    logger.info(f"Received event motion_report with a trace id of {body.get("trace_id")}")    

    event = Motion(
        station_id=body["station_id"],
        station_name=body["station_name"],
        station_location=body["station_location"],
        animal_speed=body["animal_speed"],
        picture=body["picture"],
        batch_timestamp=datetime.fromisoformat(
            body["batch_timestamp"].replace("Z", "+00:00")
        ),
        recorded_timestamp=datetime.fromisoformat(
            body["recorded_timestamp"].replace("Z", "+00:00")
        ),
        trace_id=body.get("trace_id")  
    )
    session.add(event)
    session.commit()
    session.close()
    logger.debug("Stored event motion_report with a trace id of %s",body["trace_id"])


def get_temperature_readings(start_timestamp, end_timestamp):
    """ Gets new temperature readings between the start and end timestamps """

    session = make_session()

    start = datetime.fromisoformat(start_timestamp.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_timestamp.replace("Z", "+00:00"))

    statement = (
        select(Temperature)
        .where(Temperature.date_created >= start)
        .where(Temperature.date_created < end)
    )

    results = [
        result.to_dict()
        for result in session.execute(statement).scalars().all()
    ]

    session.close()

    logger.debug(
        "Found %d temperature readings (start: %s, end: %s)",
        len(results), start, end
    )

    return results


def get_motion_readings(start_timestamp, end_timestamp):
    """ Gets new motion readings between the start and end timestamps """

    session = make_session()

    start = datetime .fromisoformat(start_timestamp.replace("Z", "+00:00"))
    end = datetime .fromisoformat(end_timestamp.replace("Z", "+00:00"))

    statement = (
        select(Motion)
        .where(Motion.date_created >= start)
        .where(Motion.date_created < end)
    )

    results = [
        result.to_dict()
        for result in session.execute(statement).scalars().all()
    ]

    session.close()

    logger.debug(
        "Found %d motion readings (start: %s, end: %s)",
        len(results), start, end
    )

    return results

def process_message():
    """Process event messages from Kafka"""

    hostname = f"{hosts}:{port}"
    client = KafkaClient(hosts=hostname)

    kafka_topic = client.topics[str.encode(topic)]

    consumer = kafka_topic.get_simple_consumer(
        consumer_group=b'event_group',
        reset_offset_on_start=False,
        auto_offset_reset=OffsetType.LATEST
    )

    for msg in consumer:

        msg_str = msg.value.decode('utf-8')
        msg_json = json.loads(msg_str)

        logger.info("Message: %s", msg_json)

        payload = msg_json["payload"]

        if msg_json["type"] == "temperature_report":
            report_temperature_readings(payload)

        elif msg_json["type"] == "motion_report":
            report_motion_readings(payload)

        consumer.commit_offsets()

def setup_kafka_thread():
    t1= Thread(target=process_message)
    t1.daemon = True
    t1.start()
    logger.info("Kafka consumer thread started.")


    

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

application = app.app

if __name__=="__main__":
    setup_kafka_thread()
    app.run(port=8090, host="0.0.0.0")
