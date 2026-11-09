import socket
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


HOST = "127.0.0.1"
PORT = 2223

LEVELS = [
    10,
    50,
    100,
]


def connect_once():
    started = time.perf_counter()

    try:
        sock = socket.create_connection(
            (HOST, PORT),
            timeout=5,
        )

        elapsed = time.perf_counter() - started

        sock.close()

        return {
            "success": True,
            "latency": elapsed,
        }

    except Exception as exc:
        return {
            "success": False,
            "latency": None,
            "error": str(exc),
        }


def run_test(connections: int):
    started = time.perf_counter()

    results = []

    with ThreadPoolExecutor(
        max_workers=connections
    ) as executor:

        futures = [
            executor.submit(connect_once)
            for _ in range(connections)
        ]

        for future in as_completed(futures):
            results.append(
                future.result()
            )

    total_elapsed = (
        time.perf_counter() - started
    )

    successful = [
        result
        for result in results
        if result["success"]
    ]

    failed = [
        result
        for result in results
        if not result["success"]
    ]

    latencies = [
        result["latency"]
        for result in successful
    ]

    print()
    print("=" * 60)
    print(
        f"Concurrent connections: {connections}"
    )
    print("=" * 60)

    print(
        f"Success: {len(successful)}/{connections}"
    )

    print(
        f"Failed: {len(failed)}"
    )

    print(
        f"Success rate: "
        f"{len(successful) / connections * 100:.2f}%"
    )

    print(
        f"Total test time: "
        f"{total_elapsed:.3f}s"
    )

    if latencies:
        print(
            f"Average latency: "
            f"{statistics.mean(latencies) * 1000:.2f} ms"
        )

        print(
            f"Minimum latency: "
            f"{min(latencies) * 1000:.2f} ms"
        )

        print(
            f"Maximum latency: "
            f"{max(latencies) * 1000:.2f} ms"
        )

        if len(latencies) > 1:
            print(
                f"Std Dev: "
                f"{statistics.stdev(latencies) * 1000:.2f} ms"
            )

    if failed:
        print()
        print("Sample errors:")

        for result in failed[:5]:
            print(
                "-",
                result.get("error")
            )


def main():
    print("=" * 60)
    print(
        "Adaptive Cyber Deception Gateway Stress Test"
    )
    print("=" * 60)

    for connections in LEVELS:
        run_test(
            connections
        )

        time.sleep(2)


if __name__ == "__main__":
    main()
