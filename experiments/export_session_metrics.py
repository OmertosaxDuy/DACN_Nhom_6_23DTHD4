import sqlite3
import sys
from datetime import datetime
import csv
from pathlib import Path
DB_PATH = "/database/cyber_deception.db"

if len(sys.argv) != 3:
    print("Usage: python export_session_metrics.py SESSION_ID MODE")
    print("MODE must be static or adaptive")
    sys.exit(1)

session_id = sys.argv[1]
mode = sys.argv[2].lower()

if mode not in ("static", "adaptive"):
    print("Invalid mode. Use static or adaptive.")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)

session = conn.execute("""
    SELECT session_id, start_time, end_time, status
    FROM sessions
    WHERE session_id = ?
    ORDER BY id DESC
    LIMIT 1
""", (session_id,)).fetchone()

if session is None:
    print(f"Session not found: {session_id}")
    conn.close()
    sys.exit(1)

sid, start, end, status = session

duration = None
if start and end:
    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
    duration = (end_dt - start_dt).total_seconds()

commands = conn.execute("""
    SELECT command
    FROM commands
    WHERE session_id = ?
    ORDER BY timestamp
""", (session_id,)).fetchall()

print("===== SESSION METRICS =====")
print(f"Session ID: {sid}")
print(f"Status: {status}")
print(f"Start: {start}")
print(f"End: {end}")
print(f"Duration: {duration:.3f}s" if duration is not None
      else "Duration: unavailable")
print(f"Commands: {len(commands)}")

for index, (command,) in enumerate(commands, 1):
    print(f"  {index}. {command}")

csv_path = Path("/tmp/cowrie_session_metrics.csv")

headers = [
    "session_id",
    "mode",
    "start_time",
    "end_time",
    "duration_seconds",
    "command_count",
    "status",
]

records = {}

if csv_path.exists():
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("session_id"):
                records[row["session_id"]] = row

if sid in records:
    if records[sid].get("mode") != mode:
        print(
            f"[WARNING] Session {sid} already has a different mode. "
            "Keeping the original record."
        )
    else:
        print(f"[SKIPPED] Session {sid} already recorded.")
else:
    records[sid] = {
        "session_id": sid,
        "mode": mode,
        "start_time": start,
        "end_time": end,
        "duration_seconds": (
            round(duration, 3) if duration is not None else ""
        ),
        "command_count": len(commands),
        "status": status,
    }

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records.values())

    print(f"[CSV SAVED] {csv_path}")

conn.close()
