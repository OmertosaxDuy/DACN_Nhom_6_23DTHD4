from tools import (
    check_bruteforce,
    get_ip_sessions,
    get_session_activity,
    change_deception_artifact,
)

IP = "192.168.255.130"


print("=== CHECK BRUTEFORCE ===")

brute = check_bruteforce.invoke({
    "src_ip": IP
})

print(brute)


print("\n=== GET SESSIONS ===")

sessions = get_ip_sessions.invoke({
    "src_ip": IP
})

print(sessions)


if sessions["sessions"]:
    session_id = sessions["sessions"][0]["session_id"]

    print("\n=== RECENT ACTIVITY ===")

    recent = get_session_activity.invoke({
        "session_id": session_id
    })

    print(recent)

if brute["detected"] and sessions["sessions"]:
    session_id = sessions["sessions"][0]["session_id"]

    print("\n=== UPDATE DECEPTION ===")

    result = change_deception_artifact.invoke({
        "session_id": session_id,
        "artifact_name": "backup_credentials",
        "content": "username=agent_container\npassword=AdaptiveFake2026"
    })

    print(result)
