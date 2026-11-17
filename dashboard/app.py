import streamlit as st
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="LoRa Smart Street Light", page_icon="💡", layout="wide")
st.title("💡 LoRa-Based Smart Street Light")
st.caption("LoRa Nodes → Gateway → MQTT → FastAPI → SQLite + InfluxDB → Dashboard")

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=3000, key="dashboard_refresh")
except Exception:
    pass

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.sidebar.header("🔐 Gateway Login")
username = st.sidebar.text_input("Username", value="admin")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    try:
        response = requests.post(API_URL + "/login", json={"username": username, "password": password}, timeout=3)
        if response.status_code == 200:
            st.session_state.logged_in = True
            st.sidebar.success("Login successful")
        else:
            st.sidebar.error("Invalid login")
    except Exception:
        st.sidebar.error("Backend is not running")

if st.session_state.logged_in:
    st.sidebar.success("🟢 Authenticated")
else:
    st.sidebar.info("Demo login: admin / admin123")

try:
    health = requests.get(API_URL + "/health", timeout=3).json()
    backend_online = True
except Exception:
    health = {}
    backend_online = False

if backend_online:
    st.success("🟢 Backend connected")
else:
    st.error("🔴 Backend unavailable. Start FastAPI first.")

st.divider()
st.header("📡 Node Monitoring")
try:
    node_data = requests.get(API_URL + "/nodes", timeout=3).json()
except Exception:
    node_data = []

if node_data:
    st.dataframe(pd.DataFrame(node_data), use_container_width=True)
else:
    st.info("No node data available yet.")

cols = st.columns(3)
for i in range(3):
    node_id = f"NODE_0{i+1}"
    with cols[i]:
        matching = [node for node in node_data if node["node_id"] == node_id]
        if matching:
            node = matching[0]
            if node["status"] == "ONLINE":
                st.success(node_id + " ONLINE")
            else:
                st.warning(node_id + " " + node["status"])
            st.write("Location:", node["location"])
            st.write("Last seen:", node["last_seen"])
        else:
            st.warning(node_id + " OFFLINE")

st.divider()
st.header("🎛️ Remote Node Control")
if not st.session_state.logged_in:
    st.info("Login from the sidebar to send commands.")
else:
    control_cols = st.columns(3)
    for i in range(3):
        node_id = f"NODE_0{i+1}"
        with control_cols[i]:
            st.subheader(node_id)
            command = st.selectbox("Command", ["ON", "OFF", "SET_BRIGHTNESS"], key="command_" + node_id)
            brightness = st.slider("Brightness", 0, 100, 50, key="brightness_" + node_id)
            if st.button("Send Command", key="send_" + node_id):
                try:
                    response = requests.post(API_URL + f"/nodes/{node_id}/command", json={"command": command, "value": brightness}, timeout=3)
                    if response.status_code == 200:
                        st.success("Command sent")
                    else:
                        st.error(response.text)
                except Exception as error:
                    st.error("Command failed: " + str(error))

st.divider()
st.header("📨 Command History")
try:
    commands = requests.get(API_URL + "/commands", timeout=3).json()
    if commands:
        st.dataframe(pd.DataFrame(commands), use_container_width=True)
    else:
        st.info("No commands yet.")
except Exception:
    st.warning("Command history unavailable.")

st.header("📝 Event History")
try:
    events = requests.get(API_URL + "/events", timeout=3).json()
    if events:
        st.dataframe(pd.DataFrame(events), use_container_width=True)
    else:
        st.info("No events yet.")
except Exception:
    st.warning("Event history unavailable.")

st.divider()
st.header("🏗️ System Architecture")
st.code("""
ESP32 + Sensors
      |
      | LoRa
      v
 LoRa Gateway
      |
      | MQTT
      v
 MQTT Broker
      |
      +-------------------+
      |                   |
      v                   v
   FastAPI             InfluxDB
   Backend             Time Series
      |
      v
    SQLite
      |
      v
 Streamlit
 Dashboard
""", language="text")

st.divider()
st.header("📋 Project Status")
a, b, c, d = st.columns(4)
with a: st.metric("LoRa Nodes", "3")
with b: st.metric("Gateway", "1")
with c: st.metric("MQTT", "ACTIVE")
with d: st.metric("Dashboard", "ONLINE")

st.caption("Software prototype. Real ESP32 + LoRa hardware can replace the simulator later.")
