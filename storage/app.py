from datetime import datetime
import connexion
from connexion import NoContent
import functools
from db import make_session
from models import Temperature
from models import Motion




def report_temperature_readings(body):
    """Receives a temperature batch event and stores events in DB"""
    session = make_session()
    event = Temperature(
        station_id=body["station_id"],
        station_name=body["station_name"],
        temp_c=body["temperature_celsius"],
        reporting_timestamp=datetime.fromisoformat(
            body["reporting_timestamp"].replace("Z", "+00:00")
        ),
        reading_timestamp=datetime.fromisoformat(
            body["reading_timestamp"].replace("Z", "+00:00")
        ),
    )
    session.add(event)
    session.commit()
    session.close()
    return NoContent, 201

from datetime import datetime

def parse_utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def report_motion_readings(body):
    """Receives a motion detection event and stores it in DB"""
    session = make_session()

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
    )
    session.add(event)
    session.commit()
    session.close()

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