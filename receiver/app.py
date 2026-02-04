import connexion
from connexion import NoContent
import httpx
import time
import yaml
import logging
import logging.config

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f)

TEMP_STORAGE_URL = app_config['temperature']['url']
MOTION_STORAGE_URL = app_config['motion']['url']

def report_temperature_readings(body):
    """
    Receives a batch of temperature readings and posts each one
    to the storage service at /temperature.
    """
    trace_id = time.time_ns() 
    logger.info(f"Received event temperature_report with a trace id of {trace_id}")
    
    for reading in body.get("readings", []):
        reading['trace_id'] = trace_id

    last_status = 500
    
    for reading in body.get("readings", []):
        data = {
            "station_id": body["station_id"],
            "station_name": body["station_name"],
            "temperature_celsius": reading["temperature_celsius"],
            "reporting_timestamp": body["reporting_timestamp"],
            "recorded_timestamp": reading["recorded_timestamp"],
            "trace_id": trace_id 
        }

        logger.info("Sending temperature reading for event temperature_report (id: %s): %s",trace_id,data)

        r = httpx.post(TEMP_STORAGE_URL, json=data, headers={"Content-Type": "application/json"})
        last_status = r.status_code
        
        logger.info("Response for event temperature_report (id: %s) has status %s",trace_id,r.status_code)
    return NoContent, last_status

def report_motion_readings(body):
    """
    Receives a batch of motion readings and posts each one
    to the storage service at /motion.
    """
    trace_id = time.time_ns() 
    logger.info(f"Received event motion_report with a trace id of {trace_id}")    
    for reading in body.get("readings", []):
        reading['trace_id'] = trace_id

    last_status = 500
    
    for reading in body.get("readings", []):
        data = {
            "station_id": body["station_id"],
            "station_name": body["station_name"],
            "station_location":body["station_location"],
            "animal_speed": reading["animal_speed"],
            "picture": reading.get("picture", ""),
            "batch_timestamp": body["batch_timestamp"],
            "recorded_timestamp": reading["recorded_timestamp"],
            "trace_id": trace_id
        }
        logger.info("Sending motion reading for event motion report (id: %s): %s",trace_id,data)

        r = httpx.post(MOTION_STORAGE_URL, json=data, headers={"Content-Type": "application/json"})
        last_status = r.status_code
        logger.info("Response for event motion report (id: %s) has status %s",trace_id,r.status_code)

    return NoContent, last_status


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

application = app.app

if __name__ == "__main__":
    app.run(port=8010)
