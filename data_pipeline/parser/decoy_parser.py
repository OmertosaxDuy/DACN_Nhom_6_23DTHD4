import json


def load_decoy_events(file_path):
    events = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    except FileNotFoundError:
        return []

    return events


def normalize_decoy_event(event):
    return {
        "source_event_key": event.get("event_key"),
        "timestamp": event.get("timestamp"),
        "service": event.get("service"),
        "dst_port": event.get("dst_port"),
        "src_ip": event.get("src_ip"),
        "src_port": event.get("src_port"),
        "payload_preview": event.get("payload_preview"),
        "payload_hex": event.get("payload_hex"),
    }
