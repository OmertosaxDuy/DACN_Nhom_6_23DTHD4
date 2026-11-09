import time
import requests

from test_hybrid_agent import (
    TOOL_API_BASE_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    run_agent_cycle,
)

SRC_IP = "192.168.255.130"

POLL_INTERVAL = 2

last_event_signature = None


def get_latest_activity(src_ip: str) -> dict:
    response = requests.get(
        f"{TOOL_API_BASE_URL}/ips/{src_ip}/sessions",
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    sessions = data.get("sessions", [])

    if not sessions:
        return {
            "session_id": None,
            "signature": None,
        }

    latest_session = sessions[0]

    session_id = latest_session.get("session_id")

    if not session_id:
        return {
            "session_id": None,
            "signature": None,
        }

    command_response = requests.get(
        f"{TOOL_API_BASE_URL}/sessions/{session_id}/commands",
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )

    command_response.raise_for_status()

    command_data = command_response.json()

    command_count = command_data.get(
        "command_count",
        0,
    )

    signature = (
        session_id,
        command_count,
    )

    return {
        "session_id": session_id,
        "command_count": command_count,
        "signature": signature,
    }


def main():
    global last_event_signature

    print("=" * 60)
    print("Adaptive Cyber Deception - Realtime Agent")
    print(f"Watching attacker: {SRC_IP}")
    print(f"Polling interval: {POLL_INTERVAL}s")
    print("=" * 60)

    while True:
        try:
            activity = get_latest_activity(
                SRC_IP
            )

            signature = activity.get(
                "signature"
            )

            if signature is None:
                print(
                    "[WAIT] No attacker session found"
                )

            elif last_event_signature is None:
                last_event_signature = signature

                print(
                    "[INIT] Current state recorded:",
                    signature,
                )

            elif signature != last_event_signature:
                print()
                print(
                    "[NEW EVENT]",
                    last_event_signature,
                    "->",
                    signature,
                )

                started = time.perf_counter()

                run_agent_cycle(
                    SRC_IP
                )

                elapsed = (
                    time.perf_counter()
                    - started
                )

                print(
                    f"[REALTIME] Cycle latency: "
                    f"{elapsed:.2f}s"
                )

                last_event_signature = signature

            time.sleep(
                POLL_INTERVAL
            )

        except KeyboardInterrupt:
            print()
            print(
                "Realtime Agent stopped."
            )
            break

        except requests.RequestException as exc:
            print(
                f"[Tool API error] {exc}"
            )

            time.sleep(
                POLL_INTERVAL
            )

        except Exception as exc:
            print(
                f"[Agent error] {exc}"
            )

            time.sleep(
                POLL_INTERVAL
            )


if __name__ == "__main__":
    main()
