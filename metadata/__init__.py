# metadata/store.py
import json
import os
from datetime import datetime

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "metadata")
os.makedirs(BASE_DIR, exist_ok=True)

def _session_file(session_id: str) -> str:
    return os.path.join(BASE_DIR, f"{session_id}.json")

def save_message(session_id: str, role: str, text: str):
    path = _session_file(session_id)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "role": role,
        "text": text,
    }
    if os.path.exists(path):
        with open(path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0); f.truncate(); json.dump(data, f, indent=2)
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([entry], f, indent=2)

def load_session(session_id: str):
    path = _session_file(session_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
