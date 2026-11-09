from langchain_core.tools import tool

from tool_client import (
    detect_bruteforce,
    get_sessions_by_ip,
    get_recent_activity,
    update_artifact,
    get_decoy_recent,
    get_decoy_activity_by_ip,
    get_decoy_statistics,
)


@tool
def check_bruteforce(src_ip: str):
    """
    Check whether an IP address has reached
    the brute-force detection threshold.
    """
    return detect_bruteforce(src_ip)


@tool
def get_ip_sessions(src_ip: str):
    """
    Get honeypot sessions associated with an IP address.
    """
    return get_sessions_by_ip(src_ip)


@tool
def get_session_activity(session_id: str):
    """
    Get recent Cowrie activity for a session.
    """
    return get_recent_activity(session_id)


@tool
def change_deception_artifact(
    session_id: str,
    artifact_name: str,
    content: str
):
    """
    Update a controlled deception artifact.

    Allowed artifacts:
    - backup_credentials
    - db_config
    - cloud_keys
    """

    return update_artifact(
        session_id,
        artifact_name,
        content,
    )

@tool
def get_recent_decoy_activity(limit: int = 20):
    """Get recent interactions with decoy services."""
    return get_decoy_recent(limit)


@tool
def get_ip_decoy_activity(src_ip: str):
    """Get decoy service interactions associated with an IP address."""
    return get_decoy_activity_by_ip(src_ip)


@tool
def get_decoy_stats():
    """Get statistics about interactions with decoy services."""
    return get_decoy_statistics()

TOOLS = [
    check_bruteforce,
    get_ip_sessions,
    get_session_activity,
    change_deception_artifact,
    get_recent_decoy_activity,
    get_ip_decoy_activity,
    get_decoy_stats,
]
