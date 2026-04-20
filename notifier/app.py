import json
import logging
from flask import jsonify, make_response # or the framework you use

logger = logging.getLogger('notifier')
from pathlib import Path

# Use the absolute path based on your folder structure
DATA_PATH = Path("/data/alerts.json") 

def post_alert(body):
    # 1. Extract
    alert_id = body.get("alert_id")
    
    # 2. Log
    logger.info(f"Processing alert: {alert_id}")

    # 3. Persistence (Append Logic)
    alerts_list = []
    if DATA_PATH.exists():
        with open(DATA_PATH, 'r') as f:
            alerts_list = json.load(f)
    
    alerts_list.append(body) # Add the new alert to the history

    with open(DATA_PATH, 'w') as f:
        json.dump(alerts_list, f, indent=2)

    # 4. Return tuple (Dictionary, Status Code)
    return {"message": "Alert recorded successfully"}, 201