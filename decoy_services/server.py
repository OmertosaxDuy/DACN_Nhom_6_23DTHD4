import json
import socket
import threading
import uuid

from datetime import datetime, timezone
from pathlib import Path


LOG_FILE = Path("/logs/decoy.jsonl")


SERVICES = {
    8080: {
        "name": "http",
        "response": (
            "HTTP/1.1 200 OK\r\n"
            "Server: Apache/2.4.57\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n"
            "\r\n"
            "<html>"
            "<head><title>Internal Portal</title></head>"
            "<body><h1>Internal Admin Portal</h1></body>"
            "</html>"
        ).encode()
    },

    3307: {
        "name": "database",
        "response": b"5.7.42-log FakeDB Server\r\n"
    },

    6380: {
        "name": "redis",
        "response": b"-NOAUTH Authentication required.\r\n"
    }
}


def write_log(service_name, port, addr, data):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "event_key": str(uuid.uuid4()),
        "event_type": "decoy_interaction",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service_name,
        "dst_port": port,
        "src_ip": addr[0],
        "src_port": addr[1],

        # Dùng preview để Agent đọc dễ
        "payload_preview": data[:300].decode(
            "utf-8",
            errors="replace"
        ),

        # Giữ bản hex để không mất binary probe
        "payload_hex": data[:1024].hex(),
    }

    with LOG_FILE.open(
        "a",
        encoding="utf-8"
    ) as f:
        f.write(json.dumps(event) + "\n")


def handle_client(conn, addr, port, service):
    data = b""

    try:
        conn.settimeout(3)

        try:
            data = conn.recv(1024)
        except socket.timeout:
            pass

        print(
            f"[{service['name']}] "
            f"{addr[0]}:{addr[1]} -> {data!r}",
            flush=True
        )

        write_log(
            service["name"],
            port,
            addr,
            data
        )

        conn.sendall(service["response"])

    except Exception as e:
        print(
            f"Client error: {e}",
            flush=True
        )

    finally:
        conn.close()


def run_service(port, service):
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(("0.0.0.0", port))
    server.listen(50)

    print(
        f"Decoy {service['name']} listening on {port}",
        flush=True
    )

    while True:
        conn, addr = server.accept()

        threading.Thread(
            target=handle_client,
            args=(conn, addr, port, service),
            daemon=True
        ).start()


for port, service in SERVICES.items():
    threading.Thread(
        target=run_service,
        args=(port, service),
        daemon=True
    ).start()


threading.Event().wait()
