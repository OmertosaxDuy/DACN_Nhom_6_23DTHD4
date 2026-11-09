from database.repository import (
    get_session,
    get_commands,
    get_events,
    get_login_attempts_by_ip,
    get_sessions_by_ip,
)


SESSION_ID = "6cb5f62c608f"
IP = "192.168.255.130"


print("SESSION:")
print(get_session(SESSION_ID))

print("\nCOMMANDS:")
print(get_commands(SESSION_ID))

print("\nEVENTS:")
print(get_events(SESSION_ID))

print("\nLOGIN ATTEMPTS:")
print(get_login_attempts_by_ip(IP))

print("\nSESSIONS BY IP:")
print(get_sessions_by_ip(IP))
