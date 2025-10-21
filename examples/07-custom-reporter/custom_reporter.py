"""Custom CSV Reporter Example

This demonstrates creating a custom reporter that outputs evaluation results to CSV format.
"""

import csv
from pathlib import Path
from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport


class CSVReporter(BaseReporter):
    """Custom reporter that outputs results to CSV file"""
    
    def __init__(self, config: dict = None):
        """Initialize CSV reporter
        
        Args:
            config: Configuration dict with optional 'output_path'
        """
        self.config = config or {}
        self.output_path = Path(self.config.get("output_path", "./report.csv"))
        
    def generate_report(self, report: EvaluationReport):
        """Generate CSV report
        
        Args:
            report: EvaluationReport object
        """
        print(f"📊 Generating CSV report: {self.output_path}")
        
        # Prepare CSV data
        rows = []
        headers = [
            "eval_id",
            "agent_id", 
            "provider_type",
            "passed",
            "cost",
            "latency_seconds",
            "evaluators_passed",
            "evaluators_total",
        ]
        
        for test_case in report.test_cases:
            # Count evaluator results
            evaluators_passed = sum(
                1 for eval_result in test_case.evaluation_results 
                if eval_result.passed
            )
            evaluators_total = len(test_case.evaluation_results)
            
            row = {
                "eval_id": test_case.eval_id,
                "agent_id": test_case.agent_id,
                "provider_type": test_case.provider_type,
                "passed": test_case.passed,
                "cost": test_case.cost,
                "latency_seconds": test_case.time_taken,
                "evaluators_passed": evaluators_passed,
                "evaluators_total": evaluators_total,
            }
            rows.append(row)
        
        # Write CSV
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✓ CSV report saved to: {self.output_path}")
        print(f"  Total test cases: {len(rows)}")
        print(f"  Passed: {sum(1 for r in rows if r['passed'])}")
        print(f"  Failed: {sum(1 for r in rows if not r['passed'])}")
    
    def cleanup(self):
        """Cleanup resources (no-op for CSV reporter)"""
        pass
