import os
import requests


BASE_URL = os.getenv(
    "TOOL_API_BASE_URL",
    "http://localhost:8000"
)

API_KEY = os.environ["TOOL_API_KEY"]

HEADERS = {
    "X-API-Key": API_KEY
}

def get_statistics():
    response = requests.get(
        f"{BASE_URL}/statistics",
        headers=HEADERS,
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def detect_bruteforce(src_ip):
    response = requests.get(
        f"{BASE_URL}/ips/{src_ip}/bruteforce",
        headers=HEADERS,
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def get_sessions_by_ip(src_ip):
    response = requests.get(
        f"{BASE_URL}/ips/{src_ip}/sessions",
        headers=HEADERS,
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def get_recent_activity(session_id, limit=10):
    response = requests.get(
        f"{BASE_URL}/sessions/{session_id}/recent",
        params={"limit": limit},
        headers=HEADERS,
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
        headers=HEADERS,
        timeout=5
    )

    response.raise_for_status()
    return response.json()


def get_deception_history(session_id):
    response = requests.get(
        f"{BASE_URL}/sessions/{session_id}/deception-history",
        headers=HEADERS,
        timeout=5
    )
    response.raise_for_status()
    return response.json()

def get_decoy_recent(limit=20):
    response = requests.get(
        f"{BASE_URL}/decoy/recent",
        params={"limit": limit},
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_decoy_activity_by_ip(src_ip, limit=50):
    response = requests.get(
        f"{BASE_URL}/decoy/ips/{src_ip}",
        params={"limit": limit},
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_decoy_statistics():
    response = requests.get(
        f"{BASE_URL}/decoy/statistics",
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
