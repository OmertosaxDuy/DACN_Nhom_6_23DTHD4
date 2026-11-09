import time
import statistics

from agent.observation_agent import ObservationAgent
from agent.analysis_agent import AnalysisAgent
from agent.decision_agent import DecisionAgent
from agent.test_hybrid_agent import (
    build_observation,
    analyze_observation,
    parse_json_decision,
    build_safe_reason,
)


SRC_IP = "192.168.255.130"
RUNS = 5


def main():
    observer = ObservationAgent(
        build_observation
    )

    analyzer = AnalysisAgent()
    decider = DecisionAgent()

    observation_times = []
    llm_times = []
    total_times = []

    print("=" * 60)
    print("Cyber Deception Agent Benchmark")
    print(f"Runs: {RUNS}")
    print("=" * 60)

    for i in range(1, RUNS + 1):
        total_start = time.perf_counter()

        observation_start = time.perf_counter()

        observation = observer.observe(
            SRC_IP
        )

        observation_elapsed = (
            time.perf_counter()
            - observation_start
        )

        analysis = analyzer.analyze(
            observation
        )

        raw_decision, llm_elapsed = (
            analyze_observation(
                observation
            )
        )

        base_decision = (
            parse_json_decision(
                raw_decision
            )
        )

        base_decision["reason"] = (
            build_safe_reason(
                observation
            )
        )

        decider.decide(
            analysis=analysis,
            observation=observation,
            base_decision=base_decision,
        )

        total_elapsed = (
            time.perf_counter()
            - total_start
        )

        observation_times.append(
            observation_elapsed
        )

        llm_times.append(
            llm_elapsed
        )

        total_times.append(
            total_elapsed
        )

        print(
            f"[RUN {i}] "
            f"observation={observation_elapsed:.2f}s "
            f"llm={llm_elapsed:.2f}s "
            f"total={total_elapsed:.2f}s"
        )

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(
        "Observation avg:",
        f"{statistics.mean(observation_times):.2f}s"
    )

    print(
        "Observation min:",
        f"{min(observation_times):.2f}s"
    )

    print(
        "Observation max:",
        f"{max(observation_times):.2f}s"
    )

    print()

    print(
        "Qwen avg:",
        f"{statistics.mean(llm_times):.2f}s"
    )

    print(
        "Qwen min:",
        f"{min(llm_times):.2f}s"
    )

    print(
        "Qwen max:",
        f"{max(llm_times):.2f}s"
    )

    print()

    print(
        "Total avg:",
        f"{statistics.mean(total_times):.2f}s"
    )

    print(
        "Total min:",
        f"{min(total_times):.2f}s"
    )

    print(
        "Total max:",
        f"{max(total_times):.2f}s"
    )


if __name__ == "__main__":
    main()
