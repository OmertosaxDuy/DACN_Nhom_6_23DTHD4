CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    src_ip TEXT,
    src_port INTEGER,
    username TEXT,
    start_time TEXT,
    end_time TEXT,
    status TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_event_key TEXT UNIQUE,
    session_id TEXT,
    event_id TEXT,
    event_type TEXT,
    timestamp TEXT,
    src_ip TEXT,
    message TEXT
);

CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_event_key TEXT UNIQUE,
    session_id TEXT,
    timestamp TEXT,
    command TEXT
);

CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_event_key TEXT UNIQUE,
    session_id TEXT,
    timestamp TEXT,
    src_ip TEXT,
    username TEXT,
    password TEXT,
    success INTEGER
);

CREATE TABLE IF NOT EXISTS deception_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    timestamp TEXT,
    action TEXT,
    result TEXT
);

CREATE TABLE IF NOT EXISTS decoy_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_event_key TEXT UNIQUE NOT NULL,
    timestamp TEXT,
    service TEXT,
    dst_port INTEGER,
    src_ip TEXT,
    src_port INTEGER,
    payload_preview TEXT,
    payload_hex TEXT
);

CREATE TABLE IF NOT EXISTS security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    src_ip TEXT,
    category TEXT,
    action TEXT,
    result TEXT,
    detail TEXT
);

CREATE TABLE IF NOT EXISTS monitoring_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    src_ip TEXT NOT NULL,
    level TEXT NOT NULL,
    reason TEXT,
    active INTEGER DEFAULT 1
);
