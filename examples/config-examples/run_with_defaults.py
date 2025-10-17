#!/usr/bin/env python3
"""
Example: Using Default Configuration

This example shows how to use the minimal config approach that leverages
the default configuration file (.judge_llm.defaults.yaml).

Benefits:
- Cleaner, more concise config files
- Automatically inherits sensible defaults
- Easy to maintain across projects
"""

from judge_llm import evaluate


def main():
    print("=" * 80)
    print("Running Evaluation with Default Configuration")
    print("=" * 80)
    print()
    print("This example uses config-with-defaults.yaml which is minimal and")
    print("inherits most settings from .judge_llm.defaults.yaml")
    print()

    # Run evaluation with defaults enabled (default behavior)
    result = evaluate(
        config="config-with-defaults.yaml",
        use_defaults=True  # This is the default, can be omitted
    )

    print()
    print("=" * 80)
    print("Evaluation Summary")
    print("=" * 80)
    print(f"Total Executions: {len(result.execution_runs)}")
    print(f"Success Rate: {result.success_rate * 100:.1f}%")
    print(f"Total Cost: ${result.total_cost:.4f}")
    print(f"Total Time: {result.total_time:.2f}s")
    print(f"Overall Success: {'✓ PASSED' if result.overall_success else '✗ FAILED'}")


if __name__ == "__main__":
    main()
