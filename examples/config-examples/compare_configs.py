#!/usr/bin/env python3
"""
Example: Comparing Default vs Full Configuration

This example demonstrates the difference between using defaults
and full configuration by running the same evaluation both ways.
"""

from judge_llm import evaluate
import json


def print_separator(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    print_separator("Comparing Default vs Full Configuration")

    # Approach 1: Using defaults (minimal config)
    print_separator("APPROACH 1: Minimal Config with Defaults")
    print("Using: config-with-defaults.yaml")
    print("Merges with: .judge_llm.defaults.yaml\n")

    result_with_defaults = evaluate(
        config="config-with-defaults.yaml",
        use_defaults=True
    )

    print(f"\n✓ Completed - Success Rate: {result_with_defaults.success_rate * 100:.1f}%")

    # Approach 2: Full configuration (no defaults)
    print_separator("APPROACH 2: Full Configuration (No Defaults)")
    print("Using: config-full.yaml")
    print("Self-contained, no default merging\n")

    result_full_config = evaluate(
        config="config-full.yaml",
        use_defaults=False
    )

    print(f"\n✓ Completed - Success Rate: {result_full_config.success_rate * 100:.1f}%")

    # Compare results
    print_separator("Comparison")

    comparison = {
        "Metric": ["Total Executions", "Success Rate", "Total Cost", "Total Time", "Overall Success"],
        "With Defaults": [
            len(result_with_defaults.execution_runs),
            f"{result_with_defaults.success_rate * 100:.1f}%",
            f"${result_with_defaults.total_cost:.4f}",
            f"{result_with_defaults.total_time:.2f}s",
            "✓ PASSED" if result_with_defaults.overall_success else "✗ FAILED"
        ],
        "Full Config": [
            len(result_full_config.execution_runs),
            f"{result_full_config.success_rate * 100:.1f}%",
            f"${result_full_config.total_cost:.4f}",
            f"{result_full_config.total_time:.2f}s",
            "✓ PASSED" if result_full_config.overall_success else "✗ FAILED"
        ]
    }

    # Print comparison table
    print(f"{'Metric':<20} | {'With Defaults':<20} | {'Full Config':<20}")
    print("-" * 66)
    for i, metric in enumerate(comparison["Metric"]):
        print(f"{metric:<20} | {comparison['With Defaults'][i]:<20} | {comparison['Full Config'][i]:<20}")

    print_separator("Conclusion")
    print("Both approaches produce the same results when configured equivalently.")
    print("Choose based on your preference:")
    print("  • Use Defaults: For cleaner, more maintainable configs")
    print("  • Full Config: For complete control and self-documentation")


if __name__ == "__main__":
    main()
