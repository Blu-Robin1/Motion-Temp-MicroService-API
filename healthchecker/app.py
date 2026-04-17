from datetime import datetime
import connexion
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
import logging
import logging.config
from pathlib import Path
import yaml

# Configure logging
with open('../config/health_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

# Load app config
with open('../config/health_config.yml', 'r') as f:
    app_config = yaml.safe_load(f)

POLL_INTERVAL = app_config['scheduler']['interval']  # in seconds, e.g., 30
STATUS_FILE = app_config['status_file_name']['name']

# Services to poll
SERVICES = app_config['services']

TIMEOUT = 3  # seconds timeout for health checks

def load_statuses():
    if not Path(STATUS_FILE).exists():
        return {}
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning("Status file corrupted or empty, resetting.")
        return {}

def save_statuses(statuses):
    with open(STATUS_FILE, 'w') as f:
        json.dump(statuses, f, indent=2)

def poll_service(name, url):
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        if resp.status_code == 200:
            status = "Up"
        else:
            status = "Down"
    except requests.RequestException as e:
        logger.error(f"Health check for {name} failed: {e}")
        status = "Down"
    return status

def update_statuses():
    logger.info("Starting health check polling cycle")
    statuses = load_statuses()

    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    service_statuses = {}

    for service_name, url in SERVICES.items():
        status = poll_service(service_name, url)
        service_statuses[service_name] = status
        logger.info(f"Service {service_name} is {status}")

    # Compose final output with all statuses and a shared last_update
    output = {
        **service_statuses,
        "last_update": now
    }

    save_statuses(output)
    logger.info("Health check polling cycle completed")

def init_scheduler(interval):
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(update_statuses, 'interval', seconds=interval)
    sched.start()

# Connexion app setup
app = connexion.FlaskApp(__name__, specification_dir='')

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# API endpoint to get current statuses
def get_status():
    logger.info("Received request for current service statuses")
    statuses = load_statuses()
    if not statuses:
        return {"message": "No status data available"}, 404
    return statuses, 200

app.add_api("openapi.yml", strict_validation=True, validate_responses=True, base_path="/health")

if __name__ == "__main__":
    update_statuses()  # Initial run before scheduler starts
    init_scheduler(POLL_INTERVAL)
    app.run(port=8120, host="0.0.0.0")
