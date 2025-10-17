#!/usr/bin/env python3
"""
Example script to run Gemini provider evaluation programmatically.

This demonstrates using the Judge LLM Python API directly instead of CLI.
"""

import os
import sys
from pathlib import Path

# Make sure judge_llm is importable (if not installed)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from judge_llm import evaluate


def main():
    """Run Gemini provider evaluation"""

    # Check if API key is set
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set it with: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)

    print("Starting Gemini evaluation...\n")

    # Method 1: Load from YAML config file
    print("Method 1: Loading from config.yaml")
    result = evaluate(config="config.yaml")

    print(f"\n✓ Evaluation completed!")
    print(f"  Total runs: {result.summary.total_runs}")
    print(f"  Successful: {result.summary.successful_runs}")
    print(f"  Failed: {result.summary.failed_runs}")
    print(f"  Success rate: {result.summary.success_rate:.1%}")
    print(f"  Total cost: ${result.summary.total_cost:.6f}")
    print(f"  Average latency: {result.summary.average_latency:.2f}s")
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

    print(f"Success rate: {result.summary.success_rate:.1%}")
    """


if __name__ == "__main__":
    main()
