"""Example: Programmatic reporter registration

This shows two ways to use custom reporters programmatically:
1. Register globally and use by name
2. Use directly without registration
"""

from judge_llm import evaluate, register_reporter
from custom_reporter import CSVReporter


def example_1_register_globally():
    """Example 1: Register custom reporter globally"""
    print("=" * 80)
    print("Example 1: Global Reporter Registration")
    print("=" * 80)
    
    # Register the custom reporter
    register_reporter("csv", CSVReporter)
    print("✓ Registered CSVReporter as 'csv'")
    print()
    
    # Now use it by name in configuration
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["../../tests/data/simple_evalset.json"]},
        providers=[{"type": "mock", "agent_id": "test_agent"}],
        evaluators=[{"type": "response_evaluator"}],
        reporters=[
            {"type": "console"},
            {"type": "csv", "config": {"output_path": "./global_report.csv"}},
        ],
    )
    
    print(f"\n✓ Generated {len(report.test_cases)} test case results")
    print()


def example_2_inline_usage():
    """Example 2: Use custom reporter inline (via config type: custom)"""
    print("=" * 80)
    print("Example 2: Inline Custom Reporter")
    print("=" * 80)
    
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["../../tests/data/simple_evalset.json"]},
        providers=[{"type": "mock", "agent_id": "test_agent"}],
        evaluators=[{"type": "response_evaluator"}],
        reporters=[
            {"type": "console"},
            {
                "type": "custom",
                "module_path": "./custom_reporter.py",
                "class_name": "CSVReporter",
                "config": {"output_path": "./inline_report.csv"},
            },
        ],
    )
    
    print(f"\n✓ Generated {len(report.test_cases)} test case results")
    print()


def example_3_multiple_custom():
    """Example 3: Use multiple custom reporters with different configs"""
    print("=" * 80)
    print("Example 3: Multiple Custom Reporters")
    print("=" * 80)
    
    # Register once
    register_reporter("csv", CSVReporter)
    
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["../../tests/data/simple_evalset.json"]},
        providers=[{"type": "mock", "agent_id": "test_agent"}],
        evaluators=[{"type": "response_evaluator"}],
        reporters=[
            {"type": "console"},
            {"type": "csv", "config": {"output_path": "./summary.csv"}},
            {"type": "csv", "config": {"output_path": "./detailed.csv"}},
            {"type": "json", "output_path": "./results.json"},
        ],
    )
    
    print(f"\n✓ Generated {len(report.test_cases)} test case results")
    print("✓ Created 3 different report formats (2x CSV, 1x JSON)")
    print()


if __name__ == "__main__":
    print("\n🎯 Custom Reporter Examples\n")
    
    # Run examples
    example_1_register_globally()
    example_2_inline_usage()
    example_3_multiple_custom()
    
    print("=" * 80)
    print("✅ All examples completed successfully!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - global_report.csv")
    print("  - inline_report.csv")
    print("  - summary.csv")
    print("  - detailed.csv")
    print("  - results.json")
    print()
