import socket

HOST = "127.0.0.1"
PORT = 2225

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(20)

print(f"[DECOY] Listening on {HOST}:{PORT}")

while True:
    client, addr = server.accept()

    print(
        f"[DECOY] Connection from "
        f"{addr[0]}:{addr[1]}"
    )

    client.sendall(
        b"SSH-2.0-Decoy-Mock-Service\r\n"
    )

    client.close()
