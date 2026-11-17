from fastapi import FastAPI, HTTPException
from backend.database import initialize_database, get_nodes, get_commands, get_events, save_command
from backend.models import CommandRequest, LoginRequest
from backend.mqtt_service import MQTTService

app = FastAPI(title="Smart Street Light API", version="1.0")
mqtt_service = MQTTService()

@app.on_event("startup")
def startup():
    initialize_database()
    mqtt_service.start()

@app.get("/")
def root():
    return {"system": "LoRa Smart Street Light", "status": "running"}

@app.get("/health")
def health():
    return {"backend": "ONLINE", "mqtt": "RUNNING", "database": "SQLITE", "time_series": "INFLUXDB"}

@app.get("/nodes")
def nodes():
    return get_nodes()

@app.get("/commands")
def commands():
    return get_commands()

@app.get("/events")
def events():
    return get_events()

@app.post("/login")
def login(request: LoginRequest):
    if request.username == "admin" and request.password == "admin123":
        return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/nodes/{node_id}/command")
def send_command(node_id: str, request: CommandRequest):
    if node_id not in {"NODE_01", "NODE_02", "NODE_03"}:
        raise HTTPException(status_code=404, detail="Unknown node")
    if request.command not in {"ON", "OFF", "SET_BRIGHTNESS"}:
        raise HTTPException(status_code=400, detail="Invalid command")
    save_command(node_id, request.command, request.value)
    mqtt_service.publish_command(node_id, request.command, request.value)
    return {"success": True, "node_id": node_id, "command": request.command, "value": request.value}
