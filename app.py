import connexion
from connexion import NoContent
import json
import os

MAX_BATCH_EVENTS = 5
TEMP_FILE = "temperature.json"
MOTION_FILE="motion.json"

def report_temperature_readings(body):
    """Receives a temperature batch event and stores summary data"""
    
    if os.path.exists(TEMP_FILE):
        with open(TEMP_FILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                    data={}
    else:
        data={}

    if "num_temp_batches" not in data:
        data["num_temp_batches"] = 0
    
    if "recent_batch_data" not in data:
        data["recent_batch_data"] = []

    total_temp = 0
    count = 0

    for reading in body["readings"]:   
        total_temp += reading["temperature_celsius"]
        count += 1

    avg_temp = total_temp / count if count > 0 else 0

    batch_summary = {
        "temp_average_celcius": avg_temp,
        "num_temp_readings": count,
        "received_timestamp": body["reporting_timestamp"]
    }

    # Update counts and queue
    data["num_temp_batches"] += 1
    data["recent_batch_data"].append(batch_summary)

    # Enforce fixed-size queue
    while len(data["recent_batch_data"]) > MAX_BATCH_EVENTS:
        data["recent_batch_data"].pop(0)
    

    #Write back to file
    with open(TEMP_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return NoContent, 201




def report_motion_readings(body):
    """Recieves a motion detection reading batch event"""

    if os.path.exists(MOTION_FILE):
        with open(MOTION_FILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                    data={}
    else:
        data ={}

    if "num_motion_batches" not in data:
        data["num_motion_batches"] = 0
    
    if "recent_batch_data" not in data:
        data["recent_batch_data"] = []

    total_motion_reading = 0
    count = 0

    for readings in body["readings"]:
        total_motion_reading += readings["animal_speed"]
        count += 1

    avg_motion_reading = total_motion_reading / count if count > 0 else 0

    batch_summary = {
        "motion_average_m/s": avg_motion_reading,
        "num_motion_readings": count,
        "received_timestamp": body["reporting_timestamp"]
    }

    # Update counts and queue
    data["num_motion_batches"] += 1
    data["recent_batch_data"].append(batch_summary)

    # Enforce fixed-size queue
    while len(data["recent_batch_data"]) > MAX_BATCH_EVENTS:
        data["recent_batch_data"].pop(0)
    

    #Write back to file
    with open(MOTION_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return NoContent,201



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

application = app.app

if __name__=="__main__":
    app.run(port=8080)