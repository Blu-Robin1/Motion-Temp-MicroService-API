from datetime import datetime
import connexion
from connexion import NoContent
from db import make_session
from models import Temperature, Motion
import yaml
import logging
import logging.config
from sqlalchemy import select


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def report_temperature_readings(body):
    """Receives a temperature batch event and stores events in DB"""
    session = make_session()
    logger.info(f"Received event temperature_report with a trace id of {body.get("trace_id")}")

    event = Temperature(
        station_id=body["station_id"],
        station_name=body["station_name"],
        temp_c=body["temperature_celsius"],
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
    return NoContent, 201

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

    return NoContent, 201

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











app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

application = app.app

if __name__=="__main__":
    app.run(port=8090)
