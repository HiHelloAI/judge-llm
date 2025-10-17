#!/usr/bin/env python3
"""
Example: Debug Configuration Loading

This example enables DEBUG logging to show exactly how the configuration
is loaded and merged with defaults in real-time.
"""

import logging
from judge_llm import evaluate
from judge_llm.utils.logger import set_log_level


def print_header(title):
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100 + "\n")


def main():
    print_header("DEBUG: Configuration Loading and Merging")

    print("This example will show you the internal config loading process.")
    print("Watch for messages about:")
    print("  • Loading default configuration")
    print("  • Loading user configuration")
    print("  • Merging configurations")
    print()
    input("Press ENTER to start evaluation with DEBUG logging enabled...")

    # Enable DEBUG logging to see config loading details
    set_log_level("DEBUG")

    print_header("RUNNING EVALUATION WITH DEBUG LOGGING")

    # Run evaluation - you'll see detailed logging of config loading
    result = evaluate(
        config="config-with-defaults.yaml",
        use_defaults=True
    )

    print_header("EVALUATION COMPLETED")
    print(f"✓ Success Rate: {result.success_rate * 100:.1f}%")
    print(f"✓ Total Executions: {len(result.execution_runs)}")
    print()
    print("Review the logs above to see how configs were loaded and merged!")


if __name__ == "__main__":
    main()
