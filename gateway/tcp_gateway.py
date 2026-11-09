import socket
import threading
from gateway.routing_state import get_routing_state
TEST_ROUTE = None

GATEWAY_HOST = "0.0.0.0"
GATEWAY_PORT = 2223

BACKENDS = {
    "allow_normal": (
        "127.0.0.1",
        2224,
    ),
    "route_to_decoy": (
        "127.0.0.1",
        2225,
    ),
    "route_to_honeypot": (
        "127.0.0.1",
        2222,
    ),
}

def pipe(source, destination):
    try:
        while True:
            data = source.recv(4096)

            if not data:
                break

            destination.sendall(data)

    except OSError:
        pass

    finally:
        try:
            destination.shutdown(socket.SHUT_WR)
        except OSError:
            pass

def handle_client(client_socket, client_address):
    print(
        f"[GATEWAY] Connection from "
        f"{client_address[0]}:{client_address[1]}"
    )

    source_ip = client_address[0]

    # Gateway chỉ đọc routing state đã được Agent tạo trước đó
    state = get_routing_state(
        source_ip
    )

    route = state.get(
        "route",
        "allow_normal",
    )

    risk_score = state.get(
        "risk_score",
        0,
    )

    risk_level = state.get(
        "risk_level",
        "low",
    )

    last_session_id = state.get(
        "last_session_id"
    )

    # Fallback an toàn nếu state chứa route không hợp lệ
    if route not in BACKENDS:
        print(
            f"[STATE WARNING] Unknown route={route}; "
            "fallback to allow_normal"
        )

        route = "allow_normal"
        risk_score = 0
        risk_level = "low"

    backend_host, backend_port = BACKENDS[
        route
    ]

    print(
        f"[STATE] src_ip={source_ip} "
        f"session={last_session_id} "
        f"score={risk_score} "
        f"level={risk_level} "
        f"route={route}"
    )

    print(
        f"[GATEWAY] Forwarding "
        f"route={route} to "
        f"{backend_host}:{backend_port}"
    )

    upstream = None

    try:
        upstream = socket.create_connection(
            (
                backend_host,
                backend_port,
            ),
            timeout=10,
        )

        client_to_upstream = threading.Thread(
            target=pipe,
            args=(
                client_socket,
                upstream,
            ),
            daemon=True,
        )

        upstream_to_client = threading.Thread(
            target=pipe,
            args=(
                upstream,
                client_socket,
            ),
            daemon=True,
        )

        client_to_upstream.start()
        upstream_to_client.start()

        client_to_upstream.join()
        upstream_to_client.join()

    except Exception as exc:
        print(
            f"[GATEWAY ERROR] {exc}"
        )

    finally:
        try:
            client_socket.close()
        except OSError:
            pass

        if upstream is not None:
            try:
                upstream.close()
            except OSError:
                pass

        print(
            f"[GATEWAY] Connection closed: "
            f"{client_address[0]}:"
            f"{client_address[1]}"
        )

def main():
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1,
    )

    server.bind(
        (GATEWAY_HOST, GATEWAY_PORT)
    )

    server.listen(50)

    print("=" * 60)
    print("Adaptive Cyber Deception TCP Gateway")
    print(
        f"Listening on "
        f"{GATEWAY_HOST}:{GATEWAY_PORT}"
    )
    print("Routing backends:")
    for route, backend in BACKENDS.items():
        print(
              f"  {route} -> "
              f"{backend[0]}:{backend[1]}"
        )
    print("=" * 60)

    try:
        while True:
            client_socket, client_address = (
                server.accept()
            )

            thread = threading.Thread(
                target=handle_client,
                args=(
                    client_socket,
                    client_address,
                ),
                daemon=True,
            )

            thread.start()

    except KeyboardInterrupt:
        print()
        print("Gateway stopped.")

    finally:
        server.close()


if __name__ == "__main__":
    main()
