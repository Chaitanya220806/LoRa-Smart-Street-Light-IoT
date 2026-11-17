import os
import sqlite3
from datetime import datetime
from config.settings import DB_FILE

os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql")

def get_connection():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    with get_connection() as connection:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as file:
            connection.executescript(file.read())
        nodes = [
            ("NODE_01", "Street Light 01", "Sector A"),
            ("NODE_02", "Street Light 02", "Sector B"),
            ("NODE_03", "Street Light 03", "Sector C"),
        ]
        for node in nodes:
            connection.execute(
                "INSERT OR IGNORE INTO nodes (node_id,name,location,status) VALUES (?,?,?,?)",
                (node[0], node[1], node[2], "OFFLINE")
            )
        connection.commit()

def update_node(node_id, status):
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as connection:
        connection.execute("UPDATE nodes SET status=?, last_seen=? WHERE node_id=?", (status, now, node_id))
        connection.commit()

def save_command(node_id, command, value):
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as connection:
        connection.execute("INSERT INTO commands (node_id,command,value,created_at) VALUES (?,?,?,?)", (node_id, command, value, now))
        connection.commit()

def save_event(node_id, event):
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as connection:
        connection.execute("INSERT INTO events (node_id,event,created_at) VALUES (?,?,?)", (node_id, event, now))
        connection.commit()

def get_nodes():
    with get_connection() as connection:
        rows = connection.execute("SELECT node_id,name,location,status,last_seen FROM nodes ORDER BY node_id").fetchall()
    return [dict(row) for row in rows]

def get_commands(limit=50):
    with get_connection() as connection:
        rows = connection.execute("SELECT id,node_id,command,value,created_at FROM commands ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]

def get_events(limit=50):
    with get_connection() as connection:
        rows = connection.execute("SELECT id,node_id,event,created_at FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]
