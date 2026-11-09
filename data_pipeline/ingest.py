import time

from parser.cowrie_parser import load_events, normalize_event
from database.db import init_db
from database.repository import (
    save_event,
    save_command,
    save_login,
    start_session,
    update_session_login,
    close_session,
    save_decoy_event,
)

from parser.decoy_parser import (
    load_decoy_events,
    normalize_decoy_event,
)

LOG_FILE = "/cowrie-data/log/cowrie/cowrie.json"

DECOY_LOG_FILE = "/decoy-data/decoy.jsonl"

def ingest_once():
    raw_events = load_events(LOG_FILE)

    for raw_event in raw_events:
        event = normalize_event(raw_event)

        is_new = save_event(event)

        if not is_new:
            continue

        event_type = event["event_type"]

        if event_type == "connection":
            start_session(event)

        elif event_type == "login_success":
            save_login(event, True)
            update_session_login(event)

        elif event_type == "login_failed":
            save_login(event, False)

        elif event_type == "command":
            save_command(event)

        elif event_type == "session_end":
            close_session(event)

def ingest_decoy_once():
    raw_events = load_decoy_events(DECOY_LOG_FILE)

    for raw_event in raw_events:
        event = normalize_decoy_event(raw_event)
        save_decoy_event(event)


def main():
    init_db()

    print("Data pipeline started...", flush=True)

    while True:
        try:
            ingest_once()
            ingest_decoy_once()
        except Exception as e:
            print("Ingestion error:", e, flush=True)

        time.sleep(2)


if __name__ == "__main__":
    main()
