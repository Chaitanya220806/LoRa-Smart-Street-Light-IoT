# LoRa-Based Smart Street Light IoT System

Software-first prototype:
ESP32/LoRa Nodes → LoRa Gateway → MQTT → FastAPI → SQLite + InfluxDB → Streamlit

## Start

1. Install packages:
   python -m pip install -r requirements.txt

2. Start MQTT and InfluxDB (Docker Desktop required):
   docker compose up -d

3. Start backend from project root:
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

4. Start simulator in another terminal:
   python simulator/node_simulator.py

5. Start dashboard in another terminal:
   python -m streamlit run dashboard/app.py

Open http://localhost:8501

Demo dashboard login: admin / admin123

FastAPI docs: http://127.0.0.1:8000/docs

## MQTT topics

Data:
smartstreetlight/node/01/data
smartstreetlight/node/02/data
smartstreetlight/node/03/data

Commands:
smartstreetlight/node/01/command
smartstreetlight/node/02/command
smartstreetlight/node/03/command

## Notes

- SQLite database is created automatically at data/streetlight.db.
- InfluxDB stores sensor and power time-series data when InfluxDB is available.
- The current simulator represents virtual LoRa nodes. Later it can be replaced by ESP32 + LoRa hardware.
- Authentication is a demo only and should not be used as production security.
