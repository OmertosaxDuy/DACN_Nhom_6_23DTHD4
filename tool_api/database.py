import sqlite3
from datetime import datetime, timezone

DB_PATH = "/database/cyber_deception.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
        SELECT
            session_id,
            timestamp,
            username,
            password,
            success
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

def get_statistics():
    conn = get_connection()

    total_sessions = conn.execute(
        "SELECT COUNT(*) FROM sessions"
    ).fetchone()[0]

    total_commands = conn.execute(
        "SELECT COUNT(*) FROM commands"
    ).fetchone()[0]

    total_logins = conn.execute(
        "SELECT COUNT(*) FROM login_attempts"
    ).fetchone()[0]

    failed_logins = conn.execute(
        """
        SELECT COUNT(*)
        FROM login_attempts
        WHERE success = 0
        """
    ).fetchone()[0]

    unique_ips = conn.execute(
        """
        SELECT COUNT(DISTINCT src_ip)
        FROM sessions
        """
    ).fetchone()[0]

    conn.close()

    return {
        "total_sessions": total_sessions,
        "total_commands": total_commands,
        "total_login_attempts": total_logins,
        "failed_logins": failed_logins,
        "unique_ips": unique_ips,
    }

def detect_bruteforce(src_ip, threshold=5):
    conn = get_connection()

    count = conn.execute(
        """
        SELECT COUNT(*)
        FROM login_attempts
        WHERE src_ip = ?
        AND success = 0
        """,
        (src_ip,)
    ).fetchone()[0]

    conn.close()

    return {
        "src_ip": src_ip,
        "failed_attempts": count,
        "threshold": threshold,
        "detected": count >= threshold
    }

def get_recent_activity(session_id, limit=10):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT event_id, event_type, timestamp, message
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (session_id, limit)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]

def detect_bruteforce(src_ip, threshold=5):
    conn = get_connection()

    count = conn.execute(
        """
        SELECT COUNT(*)
        FROM login_attempts
        WHERE src_ip = ?
          AND success = 0
        """,
        (src_ip,)
    ).fetchone()[0]

    conn.close()

    return {
        "src_ip": src_ip,
        "failed_attempts": count,
        "threshold": threshold,
        "detected": count >= threshold
    }

def get_recent_activity(session_id, limit=10):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            event_id,
            event_type,
            timestamp,
            src_ip,
            message
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (session_id, limit)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]

def save_deception_event(session_id, timestamp, action, result):
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO deception_events (
            session_id,
            timestamp,
            action,
            result
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            session_id,
            timestamp,
            action,
            result,
        )
    )

    conn.commit()
    event_id = cursor.lastrowid
    conn.close()

    return event_id


def get_deception_history(session_id):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            session_id,
            timestamp,
            action,
            result
        FROM deception_events
        WHERE session_id = ?
        ORDER BY timestamp ASC
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]

def get_recent_decoy_events(limit=20):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            timestamp,
            service,
            dst_port,
            src_ip,
            src_port,
            payload_preview
        FROM decoy_events
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    conn.close()

    return {
        "events": [dict(row) for row in rows]
    }


def get_decoy_events_by_ip(src_ip, limit=50):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            timestamp,
            service,
            dst_port,
            src_ip,
            src_port,
            payload_preview
        FROM decoy_events
        WHERE src_ip = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (src_ip, limit)
    ).fetchall()

    conn.close()

    return {
        "src_ip": src_ip,
        "events": [dict(row) for row in rows]
    }


def get_decoy_statistics():
    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) FROM decoy_events"
    ).fetchone()[0]

    unique_ips = conn.execute(
        "SELECT COUNT(DISTINCT src_ip) FROM decoy_events"
    ).fetchone()[0]

    by_service = conn.execute(
        """
        SELECT service, COUNT(*) AS count
        FROM decoy_events
        GROUP BY service
        """
    ).fetchall()

    conn.close()

    return {
        "total_events": total,
        "unique_ips": unique_ips,
        "by_service": [
            {
                "service": row["service"],
                "count": row["count"]
            }
            for row in by_service
        ]
    }

def save_security_event(
    timestamp,
    src_ip,
    category,
    action,
    result,
    detail
):
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO security_events (
            timestamp,
            src_ip,
            category,
            action,
            result,
            detail
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            src_ip,
            category,
            action,
            result,
            detail,
        )
    )

    conn.commit()
    event_id = cursor.lastrowid
    conn.close()

    return event_id

def increase_monitoring(src_ip: str, reason: str):
    conn = get_connection()

    try:
        current = conn.execute(
            """
            SELECT
                id,
                level,
                active
            FROM monitoring_state
            WHERE src_ip = ?
              AND active = 1
            ORDER BY id DESC
            LIMIT 1
            """,
            (src_ip,),
        ).fetchone()

        if (
            current is not None
            and current["level"] == "enhanced"
            and bool(current["active"]) is True
        ):
            return {
                "id": current["id"],
                "src_ip": src_ip,
                "level": "enhanced",
                "active": True,
                "already_active": True,
            }

        cursor = conn.execute(
            """
            INSERT INTO monitoring_state (
                timestamp,
                src_ip,
                level,
                reason,
                active
            )
            VALUES (
                datetime('now'),
                ?,
                'enhanced',
                ?,
                1
            )
            """,
            (src_ip, reason),
        )

        conn.commit()

        return {
            "id": cursor.lastrowid,
            "src_ip": src_ip,
            "level": "enhanced",
            "active": True,
            "already_active": False,
        }

    finally:
        conn.close()

def get_monitoring_state(src_ip: str):
    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT
                id,
                timestamp,
                src_ip,
                level,
                reason,
                active
            FROM monitoring_state
            WHERE src_ip = ?
              AND active = 1
            ORDER BY id DESC
            LIMIT 1
            """,
            (src_ip,),
        ).fetchone()

        if row is None:
            return None

        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "src_ip": row["src_ip"],
            "level": row["level"],
            "reason": row["reason"],
            "active": bool(row["active"]),
        }

    finally:
        conn.close()

def was_artifact_applied_for_evidence(
    session_id: str,
    artifact_name: str,
    evidence_fingerprint: str,
) -> bool:
    conn = get_connection()

    try:
        expected_result = (
            f"updated:{artifact_name}:"
            f"{evidence_fingerprint}"
        )

        cursor = conn.execute(
            """
            SELECT id
            FROM deception_events
            WHERE session_id = ?
              AND action = 'update_artifact'
              AND result = ?
            LIMIT 1
            """,
            (
                session_id,
                expected_result,
            ),
        )

        return cursor.fetchone() is not None

    finally:
        conn.close()
