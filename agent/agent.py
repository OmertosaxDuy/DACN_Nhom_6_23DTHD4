from tools import (
    check_bruteforce,
    get_ip_sessions,
    get_session_activity,
    change_deception_artifact,
)


IP = "192.168.255.130"


def main():
    print("=== AGENT START ===")

    brute = check_bruteforce.invoke({
        "src_ip": IP
    })

    print("Bruteforce result:")
    print(brute)

    if not brute["detected"]:
        print("No brute-force detected.")
        return

    sessions = get_ip_sessions.invoke({
        "src_ip": IP
    })

    if not sessions["sessions"]:
        print("No sessions found.")
        return

    session_id = sessions["sessions"][0]["session_id"]

    print("Latest session:")
    print(session_id)

    recent = get_session_activity.invoke({
        "session_id": session_id
    })

    print("Recent activity:")
    print(recent)

    # Tạm thời vẫn dùng rule cứng.
    # Sau này Hoàng sẽ thay phần này bằng LLM/SLM decision.
    artifact_name = "backup_credentials"

    content = (
        "username=adaptive_agent\n"
        "password=AdaptiveAgentFake2026"
    )

    result = change_deception_artifact.invoke({
        "session_id": session_id,
        "artifact_name": artifact_name,
        "content": content,
    })

    print("Deception action:")
    print(result)

    print("=== AGENT END ===")


if __name__ == "__main__":
    main()
