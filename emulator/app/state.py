import os
from pathlib import Path

CACHE_DIR = Path("./app/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

LATEST_FILE = CACHE_DIR / "latest_values.json"

def get_latest_file_path() -> Path:
    return LATEST_FILE
