import connexion
from connexion import NoContent

def report_temperature_readings(body):
    """Recieves a temperature reading batch event"""
    # Implement Here
    return NoContent, 201

def report_motion_readings(body):
    """Recieves a motion detection reading batch event"""
    # Implement Here
    return NoContent,201

app = connexion.FlaskApi(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True,validate_responses=True)

if __name__=="__main__":
    app.run(port=8080)