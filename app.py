import connexion
from connexion import NoContent
import json

MAX_BATCH_EVENTS = 5
TEMP_FILE = "temp.json"

def report_temperature_readings(body):
    """Receives a temperature batch event and stores summary data"""
    
    open(TEMP_FILE, 'a').close()  # ensures the file exists

    #Compute batch stats
    total_temp = 0
    count = 0

    for reading in body["readings"]:   # REQUIRED loop
        total_temp += reading["temperature_celsius"]
        count += 1

    avg_temp = total_temp / count if count > 0 else 0

    batch_summary = {
        "temp_average_celcius": avg_temp,
        "num_temp_readings": count,
        "received_timestamp": body["reporting_timestamp"]
    }

    #Load existing file data
    try:
        with open(TEMP_FILE, "r") as f:
            stored_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stored_data = {
            "num_temp_batches": 0,
            "recent_batch_data": []
        }

    # Update counts and queue
    stored_data["num_temp_batches"] += 1
    stored_data["recent_batch_data"].append(batch_summary)

    # Enforce fixed-size queue
    if len(stored_data["recent_batch_data"]) > MAX_BATCH_EVENTS:
        stored_data["recent_batch_data"].pop(0)
    

    #Write back to file
    with open(TEMP_FILE, "w") as f:
        json.dump(stored_data, f, indent=2)

    return NoContent, 201




def report_motion_readings(body):
    """Recieves a motion detection reading batch event"""
    print(body)
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