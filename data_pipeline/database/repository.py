from database.db import get_connection


def build_event_key(event):
    return "|".join([
        str(event.get("event_id")),
        str(event.get("session_id")),
        str(event.get("timestamp")),
        str(event.get("command")),
    ])


def save_event(event):
    conn = get_connection()

    source_key = build_event_key(event)

    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO events (
            source_event_key,
            session_id,
            event_id,
            event_type,
            timestamp,
            src_ip,
            message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_key,
            event.get("session_id"),
            event.get("event_id"),
            event.get("event_type"),
            event.get("timestamp"),
            event.get("src_ip"),
            event.get("message"),
        )
    )

    inserted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return inserted

def save_command(event):
    conn = get_connection()

    source_key = build_event_key(event)

    conn.execute(
        """
        INSERT OR IGNORE INTO commands (
            source_event_key,
            session_id,
            timestamp,
            command
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            source_key,
            event.get("session_id"),
            event.get("timestamp"),
            event.get("command"),
        )
    )

    conn.commit()
    conn.close()

def save_login(event, success):
    conn = get_connection()

    source_key = build_event_key(event)

    conn.execute(
        """
        INSERT OR IGNORE INTO login_attempts (
            source_event_key,
            session_id,
            timestamp,
            src_ip,
            username,
            password,
            success
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_key,
            event.get("session_id"),
            event.get("timestamp"),
            event.get("src_ip"),
            event.get("username"),
            event.get("password"),
            1 if success else 0,
        )
    )

    conn.commit()
    conn.close()

def start_session(event):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO sessions (
            session_id,
            src_ip,
            src_port,
            start_time,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(session_id)
        DO UPDATE SET
            src_ip = excluded.src_ip,
            src_port = excluded.src_port,
            start_time = excluded.start_time,
            status = excluded.status
        """,
        (
            event.get("session_id"),
            event.get("src_ip"),
            event.get("src_port"),
            event.get("timestamp"),
            "active",
        )
    )

    conn.commit()
    conn.close()

def update_session_login(event):
    conn = get_connection()

    conn.execute(
        """
        UPDATE sessions
        SET username = ?
        WHERE session_id = ?
        """,
        (
            event.get("username"),
            event.get("session_id"),
        )
    )

    conn.commit()
    conn.close()

def close_session(event):
    conn = get_connection()

    conn.execute(
        """
        UPDATE sessions
        SET
            end_time = ?,
            status = ?
        WHERE session_id = ?
        """,
        (
            event.get("timestamp"),
            "closed",
            event.get("session_id"),
        )
    )

    conn.commit()
    conn.close()

def get_session(session_id):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM sessions
        WHERE session_id = ?
        """,
        (session_id,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


def get_commands(session_id):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT timestamp, command
        FROM commands
        WHERE session_id = ?
        ORDER BY timestamp ASC
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_events(session_id):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT event_id, event_type, timestamp, src_ip, message
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp ASC
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_login_attempts_by_ip(src_ip):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT session_id, timestamp, username, password, success
        FROM login_attempts
        WHERE src_ip = ?
        ORDER BY timestamp ASC
        """,
        (src_ip,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_sessions_by_ip(src_ip):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM sessions
        WHERE src_ip = ?
        ORDER BY start_time DESC
        """,
        (src_ip,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]

def save_decoy_event(event):
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO decoy_events (
            source_event_key,
            timestamp,
            service,
            dst_port,
            src_ip,
            src_port,
            payload_preview,
            payload_hex
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.get("source_event_key"),
            event.get("timestamp"),
            event.get("service"),
            event.get("dst_port"),
            event.get("src_ip"),
            event.get("src_port"),
            event.get("payload_preview"),
            event.get("payload_hex"),
        )
    )

    inserted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return inserted
