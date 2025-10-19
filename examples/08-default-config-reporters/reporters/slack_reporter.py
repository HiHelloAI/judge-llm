"""Slack Reporter - sends evaluation results to Slack"""

from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport


class SlackReporter(BaseReporter):
    """Custom Slack reporter (mock implementation)"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.webhook_url = self.config.get("webhook_url")
        self.channel = self.config.get("channel", "#general")
        
    def generate_report(self, report: EvaluationReport):
        """Generate Slack notification"""
        print(f"📱 Sending results to Slack channel: {self.channel}")
        
        # Calculate summary
        total = len(report.test_cases)
        passed = sum(1 for tc in report.test_cases if tc.passed)
        failed = total - passed
        
        # Mock Slack message (in real implementation, use requests.post)
        message = f"""
🤖 LLM Evaluation Complete
━━━━━━━━━━━━━━━━━━━━━
✅ Passed: {passed}/{total}
❌ Failed: {failed}/{total}
💰 Total Cost: ${report.total_cost:.4f}
⏱️  Total Time: {report.total_time:.2f}s
━━━━━━━━━━━━━━━━━━━━━
        """.strip()
        
        print(message)
        print(f"✓ Would send to: {self.webhook_url}")
        print("  (This is a mock - implement actual HTTP POST for production)")
    
    def cleanup(self):
        pass
