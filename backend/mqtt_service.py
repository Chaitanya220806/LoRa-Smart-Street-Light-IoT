import json
import threading
import paho.mqtt.client as mqtt
from config.settings import MQTT_HOST, MQTT_PORT, MQTT_DATA_TOPIC, MQTT_COMMAND_TOPIC, INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
from backend.database import update_node, save_event

try:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError:
    InfluxDBClient = None
    Point = None
    SYNCHRONOUS = None

class MQTTService:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="smart-streetlight-backend")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.influx_client = None
        self.write_api = None
        if InfluxDBClient is not None:
            try:
                self.influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
                self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            except Exception as error:
                print("InfluxDB unavailable:", error)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print("MQTT connected:", reason_code)
        client.subscribe(MQTT_DATA_TOPIC)

    def on_message(self, client, userdata, message):
        try:
            data = json.loads(message.payload.decode("utf-8"))
            node_id = data.get("node_id", "UNKNOWN")
            update_node(node_id, "ONLINE")
            self.save_to_influx(data)
            if data.get("motion"):
                save_event(node_id, "Motion detected")
        except Exception as error:
            print("MQTT message error:", error)

    def save_to_influx(self, data):
        if self.write_api is None or Point is None:
            return
        try:
            point = (Point("street_light")
                     .tag("node_id", data["node_id"])
                     .field("ambient_light", float(data["ambient_light"]))
                     .field("motion", int(data["motion"]))
                     .field("brightness", float(data["brightness"]))
                     .field("power", float(data["power"])))
            self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        except Exception as error:
            print("InfluxDB write error:", error)

    def publish_command(self, node_id, command, value):
        node_number = node_id.replace("NODE_", "")
        topic = MQTT_COMMAND_TOPIC.format(node_number=node_number)
        payload = {"node_id": node_id, "command": command, "value": value}
        self.client.publish(topic, json.dumps(payload))

    def start(self):
        try:
            self.client.connect(MQTT_HOST, MQTT_PORT, 60)
            thread = threading.Thread(target=self.client.loop_forever, daemon=True)
            thread.start()
            return True
        except Exception as error:
            print("MQTT connection failed:", error)
            return False
