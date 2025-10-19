"""CSV Reporter - registered in defaults, used by name"""

import csv
from pathlib import Path
from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport


class CSVReporter(BaseReporter):
    """Custom CSV reporter"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.output_path = Path(self.config.get("output_path", "./report.csv"))
        
    def generate_report(self, report: EvaluationReport):
        """Generate CSV report"""
        print(f"📊 Generating CSV report: {self.output_path}")
        
        rows = []
        headers = ["eval_id", "agent_id", "passed", "cost", "latency"]
        
        for test_case in report.test_cases:
            rows.append({
                "eval_id": test_case.eval_id,
                "agent_id": test_case.agent_id,
                "passed": test_case.passed,
                "cost": test_case.cost,
                "latency": test_case.time_taken,
            })
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✓ CSV saved: {self.output_path}")
    
    def cleanup(self):
        pass
