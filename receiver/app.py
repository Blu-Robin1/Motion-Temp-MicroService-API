import connexion
from connexion import NoContent
import httpx

TEMP_STORAGE_URL = "http://localhost:8090/motiontemp/temperature"
MOTION_STORAGE_URL = "http://localhost:8090/motiontemp/motion"


def report_temperature_readings(body):
    """
    Receives a batch of temperature readings and posts each one
    to the storage service at /temperature.
    """
    last_status = 500
    for reading in body.get("readings", []):
        data = {
            "station_id": body["station_id"],
            "station_name": body["station_name"],
            "temperature_celsius": reading["temperature_celsius"],
            "reporting_timestamp": body["reporting_timestamp"],
            "reading_timestamp": reading["recorded_timestamp"]
        }

        r = httpx.post(TEMP_STORAGE_URL, json=data, headers={"Content-Type": "application/json"})
        last_status = r.status_code

    return NoContent, last_status

def report_motion_readings(body):
    """
    Receives a batch of motion readings and posts each one
    to the storage service at /motion.
    """
    last_status = 500  

    for reading in body.get("readings", []):
        data = {
            "station_id": body["station_id"],
            "station_name": body["station_name"],
            "station_location":body["station_location"],
            "animal_speed": reading["animal_speed"],
            "picture": reading.get("picture", ""),
            "batch_timestamp": body["batch_timestamp"],
            "recorded_timestamp": reading["recorded_timestamp"]
        }

        r = httpx.post(MOTION_STORAGE_URL, json=data, headers={"Content-Type": "application/json"})
        last_status = r.status_code

    return NoContent, last_status


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

application = app.app

if __name__ == "__main__":
    app.run(port=8080)
