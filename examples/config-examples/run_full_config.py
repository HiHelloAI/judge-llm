#!/usr/bin/env python3
"""
Example: Using Full Configuration

This example shows how to use a complete, self-contained configuration
without relying on default values.

Benefits:
- Full control over all settings
- Self-documenting (all options visible)
- No hidden dependencies on defaults
- Easier to understand exact behavior
"""

from judge_llm import evaluate


def main():
    print("=" * 80)
    print("Running Evaluation with Full Configuration")
    print("=" * 80)
    print()
    print("This example uses config-full.yaml which explicitly defines")
    print("all configuration values without relying on defaults.")
    print()

    # Run evaluation with defaults disabled
    result = evaluate(
        config="config-full.yaml",
        use_defaults=False  # Explicitly disable default merging
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
