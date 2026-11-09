import json


def load_events(file_path):
    events = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return events


def classify_event(event):
    event_id = event.get("eventid", "")

    if "session.connect" in event_id:
        return "connection"

    if "login.success" in event_id:
        return "login_success"

    if "login.failed" in event_id:
        return "login_failed"

    if "command.input" in event_id:
        return "command"

    if "session.closed" in event_id:
        return "session_end"

    return "other"


def normalize_event(event):
    return {
        "event_id": event.get("eventid"),
        "event_type": classify_event(event),
        "timestamp": event.get("timestamp"),
        "session_id": event.get("session"),
        "src_ip": event.get("src_ip"),
        "src_port": event.get("src_port"),
        "username": event.get("username"),
        "password": event.get("password"),
        "command": event.get("input"),
        "message": event.get("message"),
    }
