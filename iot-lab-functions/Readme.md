# IoT Functions (Azure)

This branch contains the **Azure Functions** code for processing IoT sensor data.  
It implements ingestion, validation, storage, and Dead Letter Queue (DLQ) handling.

---

## 📂 Structure
- `SensorDataIngestion` — HTTP trigger for receiving sensor data from the emulator.  
- `ProcessSensorData` — Event Hub trigger for validating and storing sensor data.  
- `GetSensorHistory` — HTTP trigger for querying historical sensor data from Cosmos DB.  
- `shared/` — shared utilities (validation, DLQ handling, logging).  

---

## ⚙️ Functions Overview

### 1. SensorDataIngestion (HTTP trigger)
- **Purpose:** Receives POST requests from the emulator.  
- **Logic:**  
  - Validates payload (required fields).  
  - If valid → forwards to Event Hub `...`.  
  - If invalid → returns HTTP 400.  

### 2. ProcessSensorData (Event Hub trigger)
- **Purpose:** Processes new events from `...`.  
- **Logic:**  
  - Normalizes keys (`sensor_id → sensorId`, `sensor_type → sensorType`).  
  - Generates `id` and `timestamp` if missing.  
  - Validates required fields (`sensorId`, `sensorType`, `value`, `unit`).  
  - If valid → writes to Cosmos DB.  
  - If invalid → sends to DLQ (`...-dlq`).  

### 3. GetSensorHistory (HTTP trigger)
- **Purpose:** Query sensor history from Cosmos DB.  
- **Parameters:**  
  - `sensorType` — filter by type.  
  - `sensorId` — filter by sensor.  
  - `hours` — time window (default 24h).  
  - `limit` — max records (default 100).  
- **Logic:**  
  - Executes query with filters.  
  - Returns sorted results (`ORDER BY timestamp DESC`).  

---

## 🧪 Testing
- **Valid data:** Sent from emulator → ingested → processed → stored in Cosmos DB.  
- **Invalid data:** Triggered via `/send_bad` in emulator → redirected to DLQ.  
- **Verification:**  
  - Logs show DLQ events (`🚫 Sent to DLQ`).  
  - Event Hub Capture contains DLQ messages.  
  - Cosmos DB contains only valid sensor readings.  

---

## 📌 Purpose
This branch demonstrates the backend pipeline for IoT data:  
**Emulator → SensorDataIngestion → Event Hub → ProcessSensorData → Cosmos DB / DLQ → GetSensorHistory.**

It ensures reliable ingestion, validation, error handling, and query capabilities for IoT sensor data.

