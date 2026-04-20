import json
import logging

logger = logging.getLogger('notifier')
from pathlib import Path

DATA_PATH = Path("/data/alerts.json") 

def post_alert(body):
    alert_id = body.get("alert_id")
    
    logger.info(f"Processing alert: {alert_id}")

    alerts_list = []
    if DATA_PATH.exists():
        with open(DATA_PATH, 'r') as f:
            alerts_list = json.load(f)
    
    alerts_list.append(body) 

    with open(DATA_PATH, 'w') as f:
        json.dump(alerts_list, f, indent=2)

    return {"message": "Alert recorded successfully"}, 201