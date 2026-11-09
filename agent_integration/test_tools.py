from tool_client import (
    detect_bruteforce,
    get_sessions_by_ip,
    get_recent_activity,
)


IP = "192.168.255.130"


print("Bruteforce:")
print(detect_bruteforce(IP))

print("\nSessions:")
sessions = get_sessions_by_ip(IP)
print(sessions)

if sessions["sessions"]:
    session_id = sessions["sessions"][0]["session_id"]

    print("\nRecent activity:")
    print(get_recent_activity(session_id))

from tool_client import update_artifact

print("\nUpdate artifact:")

result = update_artifact(
    session_id="e6addc70efcc",
    artifact_name="backup_credentials",
    content="username=agent_demo\npassword=AgentFake2026"
)

print(result)
