import time
import json
import random
import requests
import os
import sys
from datetime import datetime
from pathlib import Path

REST_API_URL = os.environ.get(
    "REST_API_URL",
    "https://iot-lab-function-avbrgmazd7gtahdk.westeurope-01.azurewebsites.net/api/sensor-data"
)

# from app.state import get_latest_file_path, CACHE_DIR
try:
    from app.state import get_latest_file_path, CACHE_DIR
except ImportError:
    from state import get_latest_file_path, CACHE_DIR

CACHE_FILE = get_latest_file_path()
HISTORY_FILE = CACHE_DIR / "history.json"

SENSORS_CONFIG = [
    {
        "sensorId": "cloud_temp1",
        "sensorType": "temperature",
        "unit": "°C",
        "interval_range": (20, 50),
        "location": {"lat": 50.4501, "lon": 30.5234, "name": "Azure Lviv"}
    },
    {
        "sensorId": "cloud_hum1",
        "sensorType": "humidity",
        "unit": "%",
        "interval_range": (30, 70),
        "location": {"lat": 50.4501, "lon": 30.5234, "name": "Azure Lviv"}
    },
    {
        "sensorId": "cloud_air1",
        "sensorType": "air_quality",
        "unit": "AQI",
        "interval_range": (40, 100),
        "location": {"lat": 50.4501, "lon": 30.5234, "name": "Azure Lviv"}
    }
]

BAD_DATA_LIST = [
    {
        "sensor_type": "temperature", 
        "value": 25.5,
        "unit": "°C"
    },
    {
        "sensor_id": "bad_sensor1",
        "value": 30.0,
        "unit": "%"
    },
    {
        "sensor_id": "bad_sensor2",
        "sensor_type": "humidity",
        "value": "not_a_number",
        "unit": "%"
    },
    {
        "sensor_id": "bad_sensor3",
        "sensor_type": "temperature", 
        "value": -10.0,
        "unit": "°C"
    }
]

def send_bad_data():
    print("🧪 Sending bad data...")
    for i, bad_data in enumerate(BAD_DATA_LIST):
        try:
            response = requests.post(
                REST_API_URL,
                json=bad_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"🚫 Bad data {i+1}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending bad data {i+1}: {e}")

def append_to_history(entry: dict):
    history = []
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append(entry)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def generate_sensor_value(sensor_type: str) -> float:
    if random.random() < 0.1:
        if sensor_type == "temperature":
            return round(random.uniform(-50.0, 100.0), 2)  # екстремальні значення
        elif sensor_type == "humidity":
            return round(random.uniform(-10.0, 150.0), 2)  # некоректні %
        elif sensor_type == "air_quality":
            return round(random.uniform(-20.0, 500.0), 2)  # некоректний AQI
    # нормальні дані
    if sensor_type == "temperature":
        return round(random.uniform(18.0, 28.0), 2)
    elif sensor_type == "humidity":
        return round(random.uniform(40.0, 85.0), 2)
    elif sensor_type == "air_quality":
        return round(random.uniform(10.0, 150.0), 2)
    return round(random.uniform(0, 100), 2)


def send_sensor_data(sensor_config):
    timestamp = datetime.utcnow().isoformat() + "Z"
    data = {
        "sensorId": sensor_config["sensorId"],
        "sensorType": sensor_config["sensorType"],
        "value": generate_sensor_value(sensor_config["sensorType"]),
        "unit": sensor_config["unit"],
        "timestamp": timestamp,
        "location": sensor_config["location"]
    }
    try:
        response = requests.post(
            REST_API_URL,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            print(f"☁️ {data['sensorType']:12} | {data['value']:6.2f}{data['unit']:4} | OK")
        else:
            print(f"❌ {data['sensorType']:12} | HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ {data['sensorType']:12} | Error: {e}")

    # зберігаємо останнє значення у кеш
    latest = {}
    if CACHE_FILE.exists():
        try:
            latest = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            latest = {}
    latest[data["sensorId"]] = data
    CACHE_FILE.write_text(json.dumps(latest, indent=2), encoding="utf-8")

    append_to_history(data)


def run_sensor(sensor_id: str):
    sensor = next((s for s in SENSORS_CONFIG if s["sensorId"] == sensor_id), None)
    if not sensor:
        print(f"⚠️ Unknown sensor_id: {sensor_id}")
        return
    print(f"🚀 Starting emulator for {sensor_id}")
    try:
        while True:
            send_sensor_data(sensor)
            min_interval, max_interval = sensor["interval_range"]
            time.sleep(random.randint(min_interval, max_interval) / 1000.0)
    except KeyboardInterrupt:
        print(f"🛑 Emulator for {sensor_id} stopped")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_sensor(sys.argv[1])
    else:
        print("⚠️ Please provide sensor_id (cloud_temp1, cloud_hum1, cloud_air1)")
