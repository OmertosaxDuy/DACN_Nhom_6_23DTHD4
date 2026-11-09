import time
import requests
import traceback
from agent.test_hybrid_agent import (
    TOOL_API_BASE_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    build_observation,
    run_agent_cycle,
)

from agent.routing_policy import (
    decide_route,
)

from gateway.routing_state import (
    update_routing_state,
)

ATTACKER_IP = "192.168.255.130"
COWRIE_SOURCE_IP = "172.18.0.1"
POLL_INTERVAL = 2


def api_get(path: str) -> dict:
    response = requests.get(
        f"{TOOL_API_BASE_URL}{path}",
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()
    return response.json()


def get_latest_session(src_ip: str) -> dict | None:
    data = api_get(
        f"/ips/{src_ip}/sessions"
    )

    sessions = data.get("sessions", [])

    if not sessions:
        return None

    # Không phụ thuộc hoàn toàn vào thứ tự API trả về.
    # Chọn session có start_time mới nhất.
    valid_sessions = [
        session
        for session in sessions
        if session.get("session_id")
    ]

    if not valid_sessions:
        return None

    return max(
        valid_sessions,
        key=lambda session: (
            session.get("start_time") or ""
        ),
    )


def get_session_events(
    session_id: str,
) -> list[dict]:
    data = api_get(
        f"/sessions/{session_id}/events"
    )

    return data.get("events", [])


def session_has_ended(
    events: list[dict],
) -> bool:
    return any(
        event.get("event_type") == "session_end"
        for event in events
    )


def count_commands(
    events: list[dict],
) -> int:
    return sum(
        1
        for event in events
        if event.get("event_type") == "command"
    )


def get_last_event_signature(
    events: list[dict],
):
    if not events:
        return None

    latest_event = max(
        events,
        key=lambda event: (
            event.get("timestamp") or ""
        ),
    )

    # event_id không unique.
    # timestamp + event_type + message dùng làm signature.
    return (
        latest_event.get("timestamp"),
        latest_event.get("event_type"),
        latest_event.get("message"),
    )


def main():
    print("=" * 70)
    print(
        "Adaptive Cyber Deception - Realtime Session Watcher"
    )
    print(
         f"Attacker identity: {ATTACKER_IP}"
    )
    print(
        f"Cowrie observed source: {COWRIE_SOURCE_IP}"
    )
    print(
        f"Polling interval: {POLL_INTERVAL}s"
    )
    print(
        "Trigger policy: ONE AI cycle after SSH session_end"
    )
    print("=" * 70)

    watched_session_id = None
    processed_session_id = None
    last_signature = None

    while True:
        try:
            latest_session = get_latest_session(
                 COWRIE_SOURCE_IP
            )

            if latest_session is None:
                print(
                    "[WAIT] No attacker session"
                )
                time.sleep(POLL_INTERVAL)
                continue

            session_id = latest_session.get(
                "session_id"
            )

            # Phát hiện một SSH session mới
            if session_id != watched_session_id:
                watched_session_id = session_id

                print()
                print(
                    f"[SESSION] Watching new session: "
                    f"{session_id}"
                )

            # Luôn đọc telemetry của session đang theo dõi
            events = get_session_events(
                session_id
            )

            # Nếu watcher vừa khởi động và session hiện tại
            # đã kết thúc từ trước thì chỉ ghi nhận baseline,
            # không chạy AI lại.
            if (
                processed_session_id is None
                and session_has_ended(events)
                and session_id == watched_session_id
            ):
                processed_session_id = session_id

                print(
                    "[INIT] Existing ended session "
                    "recorded as baseline"
                )

            signature = get_last_event_signature(
                events
            )
            # Chỉ báo khi telemetry thay đổi
            if (
                signature is not None
                and signature != last_signature
            ):
                command_count = count_commands(
                    events
                )

                print(
                    f"[TELEMETRY] "
                    f"session={session_id} "
                    f"events={len(events)} "
                    f"commands={command_count}"
                )

                last_signature = signature

            ended = session_has_ended(
                events
            )

            # Chỉ chạy AI 1 lần / session
            if (
                ended
                and processed_session_id
                != session_id
            ):
                print()
                print(
                    f"[TRIGGER] Session ended: "
                    f"{session_id}"
                )

                started = time.perf_counter()

                if command_count > 0:
                  print(
                     "[TRIGGER] Starting AI analysis..."
                  )

                  agent_result = run_agent_cycle(
                    ATTACKER_IP,
                    preferred_session_id=session_id,
                  )
                else:
                   print( 
                      "[TRIGGER] No commands; "
                      "skipping full AI analysis"
                   )
                if command_count > 0:
                    decision = agent_result["decision"]
                    risk_score = decision["risk_score"]
                    risk_level = decision["routing_risk_level"]
                    route = decision["route"]

                else:
                    observation = build_observation(
                        ATTACKER_IP,
                        preferred_session_id=session_id,
                    )

                    facts = observation.get(
                         "derived_facts",
                         {},
                    )

                    routing = decide_route(
                        facts
                    )

                    risk_score = routing.risk_score
                    risk_level = routing.risk_level
                    route = routing.route

                update_routing_state(
                     src_ip=ATTACKER_IP,
                     session_id=session_id,
                     risk_score=risk_score,
                     risk_level=risk_level,
                     route=route,
                ) 

                print(
                    f"[ROUTING STATE] "
                    f"src_ip={ATTACKER_IP} "
                    f"session={session_id} "
                    f"score={risk_score} "
                    f"level={risk_level} "
                    f"route={route}"
                )

                elapsed = (
                    time.perf_counter()
                    - started
                )

                processed_session_id = session_id

                print()
                print(
                    f"[REALTIME] "
                    f"Completed session "
                    f"{session_id}"
                )

                print(
                    f"[REALTIME] "
                    f"Total cycle latency: "
                    f"{elapsed:.2f}s"
                )

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
                f"[Agent error] "
                f"{type(exc).__name__}: {exc}"
            )
            traceback.print_exc()

            time.sleep(
                POLL_INTERVAL
            )


if __name__ == "__main__":
    main()
