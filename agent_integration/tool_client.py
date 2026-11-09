import os
import requests


BASE_URL = os.getenv(
    "TOOL_API_BASE_URL",
    "http://localhost:8000"
)

def get_statistics():
    response = requests.get(
        f"{BASE_URL}/statistics",
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def detect_bruteforce(src_ip):
    response = requests.get(
        f"{BASE_URL}/ips/{src_ip}/bruteforce",
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def get_sessions_by_ip(src_ip):
    response = requests.get(
        f"{BASE_URL}/ips/{src_ip}/sessions",
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def get_recent_activity(session_id, limit=10):
    response = requests.get(
        f"{BASE_URL}/sessions/{session_id}/recent",
        params={"limit": limit},
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def update_artifact(
    session_id,
    artifact_name,
    content
):
    payload = {
        "session_id": session_id,
        "artifact_name": artifact_name,
        "content": content,
    }

    response = requests.post(
        f"{BASE_URL}/deception-actions/update-artifact",
        json=payload,
        timeout=5
    )

    response.raise_for_status()
    return response.json()


def get_deception_history(session_id):
    response = requests.get(
        f"{BASE_URL}/sessions/{session_id}/deception-history",
        timeout=5
    )
    response.raise_for_status()
    return response.json()
