#!/usr/bin/env python
"""
Run evaluation for Google ADK agent example.

This script demonstrates how to programmatically run evaluations
for agents built with Google's Agent Development Kit (ADK).
"""

import os
import sys
from judge_llm import evaluate
import dotenv

dotenv.load_dotenv()


def main():
    """Run the ADK agent evaluation."""
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GOOGLE_API_KEY='your-api-key'")
        sys.exit(1)

    print("=" * 80)
    print("Google ADK Agent Evaluation Example")
    print("=" * 80)
    print("Config: config.yaml")
    print("")

    try:
        # Run evaluation using config file
        print("Starting evaluation...\n")
        result = evaluate(config="config.yaml")

        # Print summary
        print("\n" + "=" * 80)
        print("Evaluation Complete!")
        print("=" * 80)
        print(f"Total runs: {len(result.execution_runs)}")
        print(f"Success rate: {result.success_rate * 100:.1f}%")
        print(f"Total cost: ${result.total_cost:.4f}")
        print(f"Total time: {result.total_time:.2f}s")
        print(f"Overall success: {result.overall_success}")
        print("")

        # Print individual case results
        print("Case Results:")
        print("-" * 80)
        for run in result.execution_runs:
            status = "✓ PASS" if run.overall_success else "✗ FAIL"
            print(
                f"{status} | {run.eval_case_id} | "
                f"Time: {run.provider_result.time_taken:.2f}s | "
                f"Evaluators: {len(run.evaluator_results)}"
            )

            # Show evaluator details
            for eval_result in run.evaluator_results:
                eval_status = "✓" if eval_result.passed else "✗"
                score_info = f"Score: {eval_result.score:.2f}" if eval_result.score is not None else ""
                print(
                    f"  {eval_status} {eval_result.evaluator_name} | {score_info}"
                )

        print("")
        print("Reports saved to:")
        print("  - JSON: reports/09-google-adk-agent/adk_report.json")
        print("  - HTML: reports/09-google-adk-agent/adk_report.html")
        print("")

        # Exit with appropriate code
        sys.exit(0 if result.overall_success else 1)

    except Exception as e:
        print(f"Evaluation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
