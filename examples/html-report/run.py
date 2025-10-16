"""HTML Report Example - Generate comprehensive HTML reports"""

from judge_llm import evaluate

if __name__ == "__main__":
    print("HTML Report Example\n")
    print("=" * 60)
    print("\nGenerating comprehensive HTML report with multiple runs...\n")

    # Run evaluation with HTML reporter
    report = evaluate(config="config.yaml")

    print(f"\nEvaluation completed!")
    print(f"Total executions: {len(report.execution_runs)}")
    print(f"Success rate: {report.success_rate:.1%}")
    print(f"Total cost: ${report.total_cost:.4f}")
    print(f"Total time: {report.total_time:.2f}s")

    print(f"\nReports generated:")
    print(f"  - Console output (above)")
    print(f"  - HTML report: ./report.html")
    print(f"  - JSON report: ./report.json")

    print(f"\nOpen report.html in your browser to view the interactive dashboard!")
