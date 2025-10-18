#!/usr/bin/env python3
"""
Evaluator Config Override Example - Run Evaluation

This example demonstrates how evaluator_config in evalset.json files
can override global evaluator settings on a per-test-case basis.

Key Features:
- Global defaults defined in config.yaml
- Per-test-case overrides in test_cases.evalset.json
- Multiple evaluators with different override strategies
- Shows how to run evaluation programmatically with config file

Run this script:
    python run_evaluation.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from judge_llm.core.evaluate import evaluate
from judge_llm.utils.logger import get_logger, set_log_level


def main():
    """Run evaluator config override example"""

    # Set up logging
    set_log_level("INFO")
    logger = get_logger()

    # Get the directory of this script
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.yaml"

    logger.info("="*80)
    logger.info("Evaluator Config Override Example")
    logger.info("="*80)
    logger.info("")
    logger.info("This example demonstrates per-test-case evaluator configuration overrides:")
    logger.info("")
    logger.info("Global Defaults (config.yaml):")
    logger.info("  - ResponseEvaluator: similarity_threshold=0.6, match_type=semantic")
    logger.info("  - LatencyEvaluator: max_latency_seconds=30")
    logger.info("  - CostEvaluator: max_cost_per_case=0.10")
    logger.info("")
    logger.info("Per-Test Overrides (test_cases.evalset.json):")
    logger.info("  - test_001: Uses global defaults")
    logger.info("  - test_002: STRICT - similarity=1.0, exact match, case-sensitive")
    logger.info("  - test_003: LENIENT - similarity=0.3, recall metric")
    logger.info("  - test_004: HIGH PRECISION - similarity=0.85, ROUGE metric")
    logger.info("  - test_005: FAST LATENCY - max_latency=5s, exact match")
    logger.info("  - test_006: EXPENSIVE - max_cost=$0.50, max_latency=120s")
    logger.info("")
    logger.info("="*80)
    logger.info("")

    # Check if config file exists
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        logger.error("Please run this script from the example directory or ensure config.yaml exists")
        return 1

    # Run evaluation using config file
    try:
        logger.info(f"Loading configuration from: {config_path}")
        logger.info("")

        report = evaluate(
            config=str(config_path),
            validate_config=True,
            use_defaults=True
        )

        # Print summary
        logger.info("")
        logger.info("="*80)
        logger.info("Evaluation Summary")
        logger.info("="*80)
        logger.info(f"Total test cases: {len(report.execution_runs)}")
        logger.info(f"Overall success: {report.overall_success}")
        logger.info("")

        # Print per-test-case results showing how overrides affected evaluation
        logger.info("Per-Test-Case Results:")
        logger.info("-"*80)

        for run in report.execution_runs:
            logger.info(f"\n{run.eval_case_id}:")
            logger.info(f"  Overall: {'✓ PASS' if run.overall_success else '✗ FAIL'}")

            # Show evaluator results
            for eval_result in run.evaluator_results:
                status = "✓ PASS" if eval_result.passed else "✗ FAIL"
                score = eval_result.details.get('similarity_score', 'N/A')

                if eval_result.evaluator_type == 'response':
                    # Extract config used from details if available
                    threshold = eval_result.details.get('threshold', 'N/A')
                    match_type = eval_result.details.get('match_type', 'N/A')
                    logger.info(f"  ResponseEvaluator: {status} (score={score:.3f}, threshold={threshold}, type={match_type})")
                elif eval_result.evaluator_type == 'latency':
                    latency = eval_result.details.get('latency_seconds', 'N/A')
                    max_latency = eval_result.details.get('max_latency_seconds', 'N/A')
                    logger.info(f"  LatencyEvaluator: {status} (latency={latency:.2f}s, max={max_latency}s)")
                elif eval_result.evaluator_type == 'cost':
                    cost = eval_result.details.get('cost', 'N/A')
                    max_cost = eval_result.details.get('max_cost', 'N/A')
                    logger.info(f"  CostEvaluator: {status} (cost=${cost:.4f}, max=${max_cost})")

        logger.info("")
        logger.info("="*80)
        logger.info("Reports Generated:")
        logger.info("="*80)

        # Show report locations
        reports_dir = script_dir.parent.parent / "reports" / "05-evaluator-config-override"
        logger.info(f"  - Console: (shown above)")
        logger.info(f"  - JSON: {reports_dir / 'report.json'}")
        logger.info(f"  - HTML: {reports_dir / 'report.html'}")
        logger.info("")
        logger.info("Open the HTML report in your browser to see detailed results!")
        logger.info("")

        return 0 if report.overall_success else 1

    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
