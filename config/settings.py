import os
from dotenv import load_dotenv

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://127.0.0.1:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "smartstreetlight-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "smartstreetlight")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "streetlight")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
MQTT_DATA_TOPIC = "smartstreetlight/node/+/data"
MQTT_COMMAND_TOPIC = "smartstreetlight/node/{node_number}/command"
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "streetlight.db")
