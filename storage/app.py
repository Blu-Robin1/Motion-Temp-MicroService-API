from datetime import datetime
import connexion
from connexion import NoContent
from db import make_session
from models import Temperature, Motion
import yaml
import logging
import logging.config


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

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

application = app.app

if __name__=="__main__":
    app.run(port=8090)
