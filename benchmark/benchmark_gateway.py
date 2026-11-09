import socket
import time
import statistics


HOST = "127.0.0.1"
PORT = 2223
RUNS = 20


def main():
    times = []

    print("=" * 60)
    print("Cyber Deception Gateway Benchmark")
    print(f"Runs: {RUNS}")
    print("=" * 60)

    for i in range(1, RUNS + 1):
        started = time.perf_counter()

        sock = socket.create_connection(
            (HOST, PORT),
            timeout=5,
        )

        elapsed = (
            time.perf_counter()
            - started
        )

        times.append(elapsed)

        sock.close()

        print(
            f"[RUN {i}] "
            f"connect={elapsed * 1000:.2f} ms"
        )

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(
        "Average:",
        f"{statistics.mean(times) * 1000:.2f} ms"
    )

    print(
        "Minimum:",
        f"{min(times) * 1000:.2f} ms"
    )

    print(
        "Maximum:",
        f"{max(times) * 1000:.2f} ms"
    )

    if len(times) > 1:
        print(
            "Std Dev:",
            f"{statistics.stdev(times) * 1000:.2f} ms"
        )


if __name__ == "__main__":
    main()
