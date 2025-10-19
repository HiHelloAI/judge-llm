"""Metrics Reporter - tracks metrics over time"""

from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport


class MetricsReporter(BaseReporter):
    """Custom metrics reporter"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        
    def generate_report(self, report: EvaluationReport):
        """Generate metrics summary"""
        print(f"📈 Metrics Summary")
        print("=" * 50)
        
        # Overall metrics
        print(f"Total Test Cases: {len(report.test_cases)}")
        print(f"Success Rate: {report.success_rate * 100:.1f}%")
        print(f"Total Cost: ${report.total_cost:.4f}")
        print(f"Total Time: {report.total_time:.2f}s")
        
        # Per-agent metrics
        from collections import defaultdict
        agent_metrics = defaultdict(lambda: {"passed": 0, "failed": 0, "cost": 0.0})
        
        for tc in report.test_cases:
            metrics = agent_metrics[tc.agent_id]
            if tc.passed:
                metrics["passed"] += 1
            else:
                metrics["failed"] += 1
            metrics["cost"] += tc.cost
        
        print("\nPer-Agent Metrics:")
        for agent_id, metrics in agent_metrics.items():
            total = metrics["passed"] + metrics["failed"]
            pass_rate = (metrics["passed"] / total * 100) if total > 0 else 0
            print(f"  {agent_id}:")
            print(f"    Pass Rate: {pass_rate:.1f}%")
            print(f"    Cost: ${metrics['cost']:.4f}")
        
        print("=" * 50)
    
    def cleanup(self):
        pass
