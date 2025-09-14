import argparse
from scenarios import cpu_starvation, downstream_latency, memory_leak

SCENARIOS = {
    "cpu_starvation": cpu_starvation.inject,
    "downstream_latency": downstream_latency.inject,
    "memory_leak": memory_leak.inject,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run eBPF-Shield Evaluation Scenarios")
    parser.add_argument("--scenario", required=True, choices=SCENARIOS.keys())
    # Add args for container name, duration, etc.
    args = parser.parse_args()

    print(f"--- Starting Scenario: {args.scenario} ---")
    # In a real script, you would start capturing metrics here.
    SCENARIOS[args.scenario]()
    # Then stop capturing and process the results.
    print(f"--- Finished Scenario: {args.scenario} ---")