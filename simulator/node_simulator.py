import json
import math
import random
import time
import paho.mqtt.client as mqtt

MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
POWER_PER_NODE = 50
nodes = {f"NODE_0{i}": {"brightness": 30, "status": "ON"} for i in range(1, 4)}

def ambient_light():
    value = int(50 + 50 * math.sin(time.time() / 10))
    return max(0, min(100, value))

def on_command(client, userdata, message):
    try:
        data = json.loads(message.payload.decode("utf-8"))
        node_id = data["node_id"]
        command = data["command"]
        value = data.get("value", 0)
        if node_id not in nodes:
            return
        if command == "ON":
            nodes[node_id]["status"] = "ON"
            nodes[node_id]["brightness"] = value if value > 0 else 100
        elif command == "OFF":
            nodes[node_id]["status"] = "OFF"
            nodes[node_id]["brightness"] = 0
        elif command == "SET_BRIGHTNESS":
            nodes[node_id]["brightness"] = value
            nodes[node_id]["status"] = "ON" if value > 0 else "OFF"
        print("Command received:", node_id, command, value)
    except Exception as error:
        print("Command error:", error)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="virtual-node-system")
client.on_message = on_command
client.connect(MQTT_HOST, MQTT_PORT, 60)
for node_id in nodes:
    client.subscribe(f"smartstreetlight/node/{node_id.replace('NODE_', '')}/command")
client.loop_start()
print("Virtual LoRa node simulator started.")

while True:
    ambient = ambient_light()
    for node_id in nodes:
        motion = random.randint(0, 1)
        # Automatic simulation. A received remote command can override this until the next automatic cycle.
        if ambient >= 60:
            nodes[node_id]["status"] = "OFF"
            nodes[node_id]["brightness"] = 0
        elif motion:
            nodes[node_id]["status"] = "ON"
            nodes[node_id]["brightness"] = 100
        elif nodes[node_id]["status"] == "OFF":
            nodes[node_id]["status"] = "ON"
            nodes[node_id]["brightness"] = 30
        brightness = nodes[node_id]["brightness"]
        power = brightness * POWER_PER_NODE / 100
        packet = {
            "node_id": node_id,
            "ambient_light": ambient,
            "motion": motion,
            "brightness": brightness,
            "power": round(power, 2),
            "status": nodes[node_id]["status"],
            "rssi": random.randint(-85, -55)
        }
        topic = f"smartstreetlight/node/{node_id.replace('NODE_', '')}/data"
        client.publish(topic, json.dumps(packet))
        print(node_id, packet)
    time.sleep(2)
