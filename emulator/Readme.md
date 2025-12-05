# IoT Sensor Emulator (FastAPI)

This branch contains the code for an **IoT sensor emulator** with a FastAPI web interface.  
The emulator allows you to start, stop, and monitor sensors, as well as send data to cloud services (Azure Functions / Event Hub).

---

## 📂 Structure
- `app/emulator.py` — logic for generating sensor data (temperature, humidity, air_quality).  
- `main.py` — FastAPI server with web interface and REST routes.  
- `app/state.py` — cache and history of the latest measurements.  
- `app/templates/index.html` — main control page for sensors.  
- `app/static/` — frontend styles and scripts.  
- `history.json` — file storing measurement history.  
- `latest.json` — cache of the latest sensor values.  

---

## ⚙️ Sensor Configuration
`emulator.py` defines three sensors:
- **Temperature**: `cloud_temp1`, °C, interval 20–50 ms  
- **Humidity**: `cloud_hum1`, %, interval 30–70 ms  
- **Air Quality**: `cloud_air1`, AQI, interval 40–100 ms  

Each sensor sends a value, timestamp, and location:
```json
"location": { "lat": 50.4501, "lon": 30.5234, "name": "Azure Lviv" }
```

---

## 🚀 Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
3. Open in browser:
   ```
   http://localhost:8000
   ```

---

## 🌐 REST Routes
- `/` — main control page.  
- `/start/{sensor_id}` — start a sensor (`cloud_temp1`, `cloud_hum1`, `cloud_air1`).  
- `/stop/{sensor_id}` — stop a sensor.  
- `/status/{sensor_id}` — check sensor status.  
- `/latest` — latest values of all sensors.  
- `/history` — full measurement history.  
- `/history/clear` — clear history.  
- `/send_bad` — send test “bad” data to the cloud.  

---

## 🧪 Testing
- Calling `/send_bad` generates invalid data (missing fields, text values, negative numbers).  
- Logs show messages about sending data to **DLQ**.  
- Data can be verified in **Event Hub Capture** and Cosmos DB.  

---

## 📌 Purpose
This emulator is used for:
- testing the IoT data pipeline (Azure Functions → Event Hub → Cosmos DB → DLQ);  
- validating error handling and data integrity;  
- demonstrating a web interface for sensor control.  

## Website view
Placed in folder /emulator – emulator_home.png

