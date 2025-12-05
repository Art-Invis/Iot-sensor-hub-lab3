# IoT Sensor Pipeline (Azure + FastAPI)

This repository contains a complete **IoT data pipeline** prototype.  
It includes a FastAPI‑based **sensor emulator** and a set of **Azure Functions** for ingestion, validation, storage, and Dead Letter Queue (DLQ) handling.

---

## 📂 Repository Structure
- **`emulator` branch** — FastAPI web interface and sensor emulator.  
- **`functions` branch** — Azure Functions for ingestion, processing, history queries, and DLQ.  
- **`main` branch** — stable integration of emulator + functions.  

---

## ⚙️ Components

### 1. Sensor Emulator (FastAPI)
- Emulates three sensors: temperature (`cloud_temp1`), humidity (`cloud_hum1`), air quality (`cloud_air1`).  
- Provides a web interface with routes for start/stop, status, latest values, history, and sending test “bad” data.  
- Location metadata included: `Azure Lviv (lat: 50.4501, lon: 30.5234)`.

### 2. Azure Functions
- **SensorDataIngestion (HTTP trigger):** receives POST requests from emulator, forwards valid data to Event Hub.  
- **ProcessSensorData (Event Hub trigger):** normalizes, validates, stores valid data in Cosmos DB, sends invalid data to DLQ.  
- **GetSensorHistory (HTTP trigger):** queries Cosmos DB with filters (`sensorType`, `sensorId`, `hours`, `limit`) and returns sorted results.

### 3. Dead Letter Queue (DLQ)
- Separate Event Hub: `iot-sensor-hub-dlq`.  
- Stores invalid or failed messages (missing fields, wrong types, negative values, JSON errors).  
- Messages include error description, original payload, and timestamp.  
- Can be reviewed via Event Hub Capture or a dedicated Cosmos DB container.

---

## 📥 How to Download / Clone

To get the repository locally:

### Clone the repo
git clone https://github.com/<your-username>/<repo-name>.git

### Navigate into the folder
cd <repo-name>

### Switch to the desired branch (emulator or functions)
git checkout emulator
### or
git checkout functions

--- 
## 🚀 Run & Test

### Emulator
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Open in browser: [http://localhost:8000](http://localhost:8000)

### Functions
Deploy to Azure Functions or run locally with Azure Functions Core Tools.  
Environment variables required: `COSMOS_URI`, `COSMOS_KEY`, `COSMOS_DB`, `COSMOS_CONTAINER`, `EVENTHUB_CONN_STR`.

### Testing
- Valid data → ingested and stored in Cosmos DB.  
- Invalid data (via `/send_bad`) → redirected to DLQ.  
- Logs show DLQ events (`🚫 Sent to DLQ`).  
- Event Hub Capture confirms DLQ messages.  

---

## 📌 Purpose
This project demonstrates a **full IoT workflow**:
**Emulator → SensorDataIngestion → Event Hub → ProcessSensorData → Cosmos DB / DLQ → GetSensorHistory**

It highlights:
- sensor emulation and web control,  
- cloud ingestion and validation,  
- reliable error handling with DLQ,  
- querying and visualization of sensor history.  

---

## 🧩 Branches
- `emulator` — FastAPI sensor emulator.  
- `functions` — Azure Functions backend.  
- `main` — integrated stable version.  

---

## 📖 License
Educational project for IoT lab work.  
Feel free to adapt and extend for your own experiments.

