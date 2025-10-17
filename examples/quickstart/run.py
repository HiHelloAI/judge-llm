"""Quickstart example - Run Judge LLM evaluation programmatically"""

from judge_llm import evaluate

if __name__ == "__main__":
    print("Running Judge LLM Quickstart Example\n")
    print("=" * 60)

    # Option 1: Run from config file
    print("\nOption 1: Running from config file...")
    report = evaluate(config="config.yaml")

    print(f"\nEvaluation completed!")
    print(f"Total executions: {len(report.execution_runs)}")
    print(f"Success rate: {report.success_rate:.1%}")
    print(f"Total cost: ${report.total_cost:.4f}")
    print(f"Total time: {report.total_time:.2f}s")

    # Option 2: Run with direct arguments (mimics config.yaml structure)
    # Uncomment to test
    """
    print("\n\nOption 2: Running with direct arguments...")
    report = evaluate(
        agent={
            "log_level": "INFO",
            "num_runs": 1,
            "parallel_execution": False,
        },
        dataset={
            "loader": "local_file",
            "paths": ["./sample.evalset.json"]
        },
        providers=[
            {
                "type": "mock",
                "agent_id": "news_agent",
                "model": "mock-model-v1",
            }
        ],
        evaluators=[
            {
                "type": "response_validator",
                "enabled": True,
                "config": {"similarity_threshold": 0.8, "match_type": "exact"},
            },
            {
                "type": "trajectory_validator",
                "enabled": True,
                "config": {"sequence_match_type": "exact"},
            },
        ],
        reporters=[
            {"type": "console"}
        ]
    )

    print(f"\nEvaluation completed!")
    print(f"Success rate: {report.success_rate:.1%}")
    """
