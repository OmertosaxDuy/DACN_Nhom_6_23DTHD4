from tools import (
    get_recent_decoy_activity,
    get_ip_decoy_activity,
    get_decoy_stats,
)


IP = "192.168.255.130"


print("=== DECOY STATISTICS ===")
print(
    get_decoy_stats.invoke({})
)


print("\n=== RECENT DECOY ACTIVITY ===")
print(
    get_recent_decoy_activity.invoke({
        "limit": 5
    })
)


print("\n=== IP DECOY ACTIVITY ===")
print(
    get_ip_decoy_activity.invoke({
        "src_ip": IP
    })
)
