from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import subprocess
import json
import sys
from pathlib import Path
from app.state import get_latest_file_path, CACHE_DIR

HISTORY_FILE = CACHE_DIR / "history.json"

app = FastAPI(title="IoT Emulator Control")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

sensor_processes = {}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/start/{sensor_id}")
def start_sensor(sensor_id: str):
    global sensor_processes
    if sensor_id not in sensor_processes or sensor_processes[sensor_id] is None or sensor_processes[sensor_id].poll() is not None:
        sensor_processes[sensor_id] = subprocess.Popen([sys.executable, "app/emulator.py", sensor_id])
        return {"status": f"{sensor_id} started"}
    return {"status": f"{sensor_id} already running"}

@app.get("/stop/{sensor_id}")
def stop_sensor(sensor_id: str):
    global sensor_processes
    if sensor_id in sensor_processes and sensor_processes[sensor_id] and sensor_processes[sensor_id].poll() is None:
        sensor_processes[sensor_id].terminate()
        sensor_processes[sensor_id] = None
        return {"status": f"{sensor_id} stopped"}
    return {"status": f"{sensor_id} not running"}

@app.get("/status/{sensor_id}")
def status(sensor_id: str):
    if sensor_id in sensor_processes and sensor_processes[sensor_id] and sensor_processes[sensor_id].poll() is None:
        return {"status": f"{sensor_id} running"}
    return {"status": f"{sensor_id} stopped"}

@app.get("/latest")
def latest():
    latest_path: Path = get_latest_file_path()
    if latest_path.exists():
        try:
            raw = json.loads(latest_path.read_text(encoding="utf-8"))
            data = {}
            for sid, doc in raw.items():
                data[sid] = {
                    "sensorId": doc.get("sensorId") or doc.get("sensor_id"),
                    "sensorType": doc.get("sensorType") or doc.get("sensor_type"),
                    "value": doc.get("value"),
                    "unit": doc.get("unit"),
                    "timestamp": doc.get("timestamp"),
                    "location": doc.get("location")
                }
            return JSONResponse(data)
        except Exception as e:
            return JSONResponse({"error": f"Failed to read cache: {e}"}, status_code=500)
    return JSONResponse({"message": "No data yet", "cache_dir": str(CACHE_DIR)}, status_code=200)


def append_to_history(entry: dict):
    history = []
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append(entry)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")

@app.get("/history")
def get_history():
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            return JSONResponse(history)
        except Exception as e:
            return JSONResponse({"error": f"Failed to read history: {e}"}, status_code=500)
    return JSONResponse([], status_code=200)

@app.post("/history/clear")
def clear_history():
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    return {"status": "history cleared"}

@app.post("/send_bad")
def send_bad():
    from app.emulator import send_bad_data
    send_bad_data()
    return {"status": "bad data sent"}
