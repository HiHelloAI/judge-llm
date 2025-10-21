#!/usr/bin/env python3
"""
Example: Using Database Reporter for Historical Tracking

This example demonstrates:
1. Running evaluations with the database reporter
2. Storing results in SQLite database
3. Querying historical results for analysis
4. Tracking trends across multiple runs

The database reporter enables:
- Historical tracking of all evaluation runs
- Cost and performance analysis
- Provider comparison
- Regression detection
- Custom queries and reporting
"""

from judge_llm.core.evaluate import evaluate


def main():
    """Run evaluation with database reporter"""

    print("=" * 80)
    print("Database Reporter Example")
    print("=" * 80)
    print()
    print("This example will:")
    print("  1. Run evaluation against Gemini provider")
    print("  2. Store results in SQLite database")
    print("  3. Generate console, database, and HTML reports")
    print()
    print("After running, you can:")
    print("  - View the HTML report in your browser")
    print("  - Query the database using the query_results.py script")
    print("  - Use SQLite tools to explore the data")
    print()
    print("=" * 80)
    print()

    # Run evaluation with database reporter
    report = evaluate(config="config.yaml")

    print()
    print("=" * 80)
    print("Evaluation Complete!")
    print("=" * 80)
    print()
    print(f"Total executions: {len(report.execution_runs)}")
    print(f"Success rate: {report.success_rate:.1%}")
    print(f"Total cost: ${report.total_cost:.4f}")
    print(f"Total time: {report.total_time:.2f}s")
    print()
    print("Reports generated:")
    print("  - Database: ../../reports/06-database-reporter/results.db")
    print("  - HTML: ../../reports/06-database-reporter/report.html")
    print()
    print("Next steps:")
    print("  1. Run this evaluation multiple times to build history")
    print("  2. Use query_results.py to analyze the database")
    print("  3. Try different providers and compare results")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
