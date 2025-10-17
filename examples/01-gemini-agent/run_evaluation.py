#!/usr/bin/env python3
"""
Example script to run Gemini provider evaluation programmatically.

This demonstrates using the Judge LLM Python API directly instead of CLI.
"""

import os
import sys
import dotenv

dotenv.load_dotenv()

from judge_llm import evaluate


def main():
    """Run Gemini provider evaluation"""

    # Check if API key is set
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GOOGLE_API_KEY='your-api-key'")
        sys.exit(1)

    print("Starting Gemini evaluation...\n")

    # Method 1: Load from YAML config file
    print("Method 1: Loading from config.yaml")
    result = evaluate(config="config.yaml")

    print(f"\n✓ Evaluation completed!")

    # Debug: Check what's in the result
    print(f"\n=== DEBUG INFO ===")
    print(f"Result type: {type(result)}")
    print(f"Result attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")

    if result.execution_runs:
        print(f"\nFirst ExecutionRun type: {type(result.execution_runs[0])}")
        print(f"ExecutionRun attributes: {[attr for attr in dir(result.execution_runs[0]) if not attr.startswith('_')]}")
        print(f"\nFirst run data: {result.execution_runs[0]}")

    print(f"\nResult summary: {result.summary}")
    print(f"Result total_cost: {result.total_cost}")
    print(f"Result total_time: {result.total_time}")
    print(f"Result success_rate: {result.success_rate}")
    print(f"Result overall_success: {result.overall_success}")
    print(f"=== END DEBUG ===\n")

    # Use the attributes directly from result object
    total_runs = len(result.execution_runs)
    successful_runs = sum(1 for run in result.execution_runs if run.overall_success)
    failed_runs = total_runs - successful_runs

    print(f"  Total runs: {total_runs}")
    print(f"  Successful: {successful_runs}")
    print(f"  Failed: {failed_runs}")
    print(f"  Success rate: {result.success_rate:.1%}")
    print(f"  Total cost: ${result.total_cost:.6f}")
    print(f"  Average latency: {result.total_time / total_runs if total_runs > 0 else 0:.2f}s")
    print(f"\n  Reports generated:")
    print(f"    - Console output (above)")
    print(f"    - JSON: gemini_report.json")
    print(f"    - HTML: gemini_report.html")

    # Method 2: Programmatic configuration (commented out)
    """
    print("\n\nMethod 2: Programmatic configuration")
    result = evaluate(
        agent={
            "name": "gemini_test",
            "log_level": "INFO",
            "num_runs": 1,
        },
        dataset={
            "loader": "local_file",
            "paths": ["./sample.evalset.json"],
        },
        providers=[
            {
                "type": "gemini",
                "agent_id": "gemini_agent",
                "model": "gemini-2.0-flash-exp",
                "temperature": 0.7,
                "max_tokens": 2048,
            }
        ],
        evaluators=[
            {
                "type": "response_validator",
                "config": {"similarity_threshold": 0.7}
            },
            {
                "type": "latency_evaluator",
                "config": {"max_latency_seconds": 30}
            },
        ],
        reporters=[
            {"type": "console"},
            {"type": "json", "output_path": "./report.json"},
        ],
    )

    print(f"Success rate: {result.summary['success_rate']:.1%}")
    """


if __name__ == "__main__":
    main()
