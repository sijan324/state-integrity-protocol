import json
from datetime import datetime

LOG_FILE = "sip_events.jsonl"


def emit_event(event: dict):
    event["timestamp"] = datetime.utcnow().isoformat()

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


def load_events(limit=50):
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()[-limit:]
            return [json.loads(l) for l in lines]
    except FileNotFoundError:
        return []