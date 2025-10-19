---
sidebar_position: 6
---

# Custom Reporters

Create your own reporters to output evaluation results in any format you need - CSV, Slack, metrics systems, and more.

## Overview

Custom reporters let you extend Judge LLM with your own output formats and integrations. Implement the simple `BaseReporter` interface to:

- Export to custom formats (CSV, Excel, Markdown)
- Send results to communication platforms (Slack, Teams, Discord)
- Push metrics to monitoring systems (Prometheus, DataDog, CloudWatch)
- Integrate with issue trackers (Jira, Linear, GitHub Issues)
- Store in custom databases (MongoDB, PostgreSQL, Redis)

## Quick Start

### 1. Create a Custom Reporter

```python
from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport
from pathlib import Path
import csv

class CSVReporter(BaseReporter):
    """Export evaluation results as CSV"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.output_path = Path(self.config.get("output_path", "./results.csv"))
    
    def generate_report(self, report: EvaluationReport):
        """Generate CSV report"""
        with open(self.output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'eval_id', 'agent_id', 'provider_type',
                'passed', 'cost', 'time_taken'
            ])
            
            # Write test cases
            for tc in report.test_cases:
                writer.writerow([
                    tc.eval_id,
                    tc.agent_id,
                    tc.provider_type,
                    tc.passed,
                    tc.cost,
                    tc.time_taken
                ])
        
        print(f"CSV report saved to {self.output_path}")
    
    def cleanup(self):
        """Cleanup resources"""
        pass
```

### 2. Register the Reporter

**Option 1: Inline Registration (Python API)**

```python
from judge_llm import evaluate, register_reporter
from my_reporters import CSVReporter

# Register once
register_reporter("csv", CSVReporter)

# Use by name
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "csv", "output_path": "./results.csv"}]
)
```

**Option 2: Config-Based Registration**

```yaml
# test.yaml
reporters:
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    output_path: ./results.csv
```

**Option 3: Default Config Registration (Recommended)**

Register once in `.judge_llm.defaults.yaml`:
```yaml
reporters:
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    register_as: csv
```

Use everywhere by name:
```yaml
# test.yaml
reporters:
  - type: csv
    output_path: ./results.csv
```

## BaseReporter Interface

All custom reporters must implement the `BaseReporter` interface:

```python
from abc import ABC, abstractmethod
from judge_llm.core.models import EvaluationReport

class BaseReporter(ABC):
    """Abstract base class for reporters"""

    @abstractmethod
    def generate_report(self, report: EvaluationReport):
        """Generate report from evaluation results
        
        Args:
            report: EvaluationReport object containing all results
        """
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup resources after report generation"""
        pass
```

### EvaluationReport Structure

```python
@dataclass
class EvaluationReport:
    total_cost: float
    total_time: float
    success_rate: float
    overall_success: bool
    summary: Dict[str, Any]  # Contains counts, aggregates
    test_cases: List[TestCaseResult]
```

### TestCaseResult Structure

```python
@dataclass
class TestCaseResult:
    eval_id: str
    agent_id: str
    provider_type: str
    passed: bool
    cost: float
    time_taken: float
    evaluation_results: List[EvaluationResult]
    conversation_history: List[Dict[str, Any]]
```

## Example Reporters

### CSV Reporter (Production-Ready)

```python
from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport
from pathlib import Path
import csv
from datetime import datetime

class CSVReporter(BaseReporter):
    """Export evaluation results as CSV with full details"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.output_path = Path(self.config.get("output_path", "./results.csv"))
        self.include_summary = self.config.get("include_summary", True)
        
    def generate_report(self, report: EvaluationReport):
        """Generate detailed CSV report"""
        # Ensure directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Summary section
            if self.include_summary:
                writer.writerow(['=== SUMMARY ==='])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Timestamp', datetime.now().isoformat()])
                writer.writerow(['Total Cost', f'${report.total_cost:.4f}'])
                writer.writerow(['Total Time', f'{report.total_time:.2f}s'])
                writer.writerow(['Success Rate', f'{report.success_rate * 100:.1f}%'])
                writer.writerow(['Total Tests', report.summary['total_executions']])
                writer.writerow(['Passed', report.summary['successful_executions']])
                writer.writerow(['Failed', report.summary['failed_executions']])
                writer.writerow([])  # Blank line
            
            # Test cases section
            writer.writerow(['=== TEST CASES ==='])
            writer.writerow([
                'Eval ID', 'Agent ID', 'Provider', 'Status',
                'Cost', 'Time (s)', 'Evaluators Passed', 'Evaluators Failed'
            ])
            
            for tc in report.test_cases:
                passed_evals = sum(1 for e in tc.evaluation_results if e.passed)
                failed_evals = len(tc.evaluation_results) - passed_evals
                
                writer.writerow([
                    tc.eval_id,
                    tc.agent_id,
                    tc.provider_type,
                    'PASS' if tc.passed else 'FAIL',
                    f'${tc.cost:.4f}',
                    f'{tc.time_taken:.2f}',
                    passed_evals,
                    failed_evals
                ])
        
        print(f"✓ CSV report saved to {self.output_path}")
    
    def cleanup(self):
        """No cleanup needed for CSV files"""
        pass
```

### Slack Reporter

```python
import requests
from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport

class SlackReporter(BaseReporter):
    """Send evaluation summary to Slack"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.webhook_url = self.config.get("webhook_url")
        self.channel = self.config.get("channel", "#evals")
        self.mention_on_failure = self.config.get("mention_on_failure", True)
        
        if not self.webhook_url:
            raise ValueError("webhook_url is required for SlackReporter")
    
    def generate_report(self, report: EvaluationReport):
        """Send summary to Slack"""
        # Build message
        status_emoji = "✅" if report.overall_success else "❌"
        status_text = "All tests passed!" if report.overall_success else "Some tests failed"
        
        message = {
            "channel": self.channel,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{status_emoji} Evaluation Results"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Status:*\n{status_text}"},
                        {"type": "mrkdwn", "text": f"*Success Rate:*\n{report.success_rate * 100:.1f}%"},
                        {"type": "mrkdwn", "text": f"*Total Cost:*\n${report.total_cost:.4f}"},
                        {"type": "mrkdwn", "text": f"*Total Time:*\n{report.total_time:.1f}s"},
                        {"type": "mrkdwn", "text": f"*Tests Passed:*\n{report.summary['successful_executions']}/{report.summary['total_executions']}"},
                        {"type": "mrkdwn", "text": f"*Tests Failed:*\n{report.summary['failed_executions']}/{report.summary['total_executions']}"}
                    ]
                }
            ]
        }
        
        # Add mention if failures
        if not report.overall_success and self.mention_on_failure:
            message["text"] = "<!channel> Evaluation failures detected"
        
        # Send to Slack
        response = requests.post(self.webhook_url, json=message)
        response.raise_for_status()
        
        print(f"✓ Results sent to Slack channel {self.channel}")
    
    def cleanup(self):
        """No cleanup needed"""
        pass
```

### Prometheus Metrics Reporter

```python
from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

class PrometheusReporter(BaseReporter):
    """Push evaluation metrics to Prometheus Pushgateway"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.pushgateway = self.config.get("pushgateway", "localhost:9091")
        self.job_name = self.config.get("job_name", "judge_llm_evals")
        self.registry = CollectorRegistry()
        
        # Define metrics
        self.success_rate = Gauge(
            'eval_success_rate',
            'Evaluation success rate',
            registry=self.registry
        )
        self.total_cost = Gauge(
            'eval_total_cost',
            'Total evaluation cost',
            registry=self.registry
        )
        self.total_time = Gauge(
            'eval_total_time_seconds',
            'Total evaluation time',
            registry=self.registry
        )
        self.test_count = Gauge(
            'eval_test_count',
            'Number of test cases',
            ['status'],
            registry=self.registry
        )
    
    def generate_report(self, report: EvaluationReport):
        """Push metrics to Prometheus"""
        # Set gauge values
        self.success_rate.set(report.success_rate)
        self.total_cost.set(report.total_cost)
        self.total_time.set(report.total_time)
        self.test_count.labels(status='passed').set(report.summary['successful_executions'])
        self.test_count.labels(status='failed').set(report.summary['failed_executions'])
        
        # Push to gateway
        push_to_gateway(
            self.pushgateway,
            job=self.job_name,
            registry=self.registry
        )
        
        print(f"✓ Metrics pushed to Prometheus at {self.pushgateway}")
    
    def cleanup(self):
        """No cleanup needed"""
        pass
```

### Markdown Reporter

```python
from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport
from pathlib import Path
from datetime import datetime

class MarkdownReporter(BaseReporter):
    """Generate Markdown report suitable for GitHub, documentation, etc."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.output_path = Path(self.config.get("output_path", "./EVAL_REPORT.md"))
        self.include_details = self.config.get("include_details", True)
    
    def generate_report(self, report: EvaluationReport):
        """Generate Markdown report"""
        lines = []
        
        # Header
        lines.append("# Evaluation Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        status = "✅ PASSED" if report.overall_success else "❌ FAILED"
        lines.append(f"**Status:** {status}")
        lines.append(f"**Success Rate:** {report.success_rate * 100:.1f}%")
        lines.append(f"**Total Cost:** ${report.total_cost:.4f}")
        lines.append(f"**Total Time:** {report.total_time:.2f}s")
        lines.append(f"**Tests:** {report.summary['successful_executions']}/{report.summary['total_executions']} passed")
        lines.append("")
        
        # Test results table
        lines.append("## Test Results")
        lines.append("")
        lines.append("| Eval ID | Agent | Provider | Status | Cost | Time |")
        lines.append("|---------|-------|----------|--------|------|------|")
        
        for tc in report.test_cases:
            status = "✅" if tc.passed else "❌"
            lines.append(
                f"| {tc.eval_id} | {tc.agent_id} | {tc.provider_type} | "
                f"{status} | ${tc.cost:.4f} | {tc.time_taken:.2f}s |"
            )
        
        lines.append("")
        
        # Details section
        if self.include_details:
            lines.append("## Detailed Results")
            lines.append("")
            
            for tc in report.test_cases:
                lines.append(f"### {tc.eval_id}")
                lines.append("")
                lines.append(f"- **Agent:** {tc.agent_id}")
                lines.append(f"- **Provider:** {tc.provider_type}")
                lines.append(f"- **Status:** {'✅ PASSED' if tc.passed else '❌ FAILED'}")
                lines.append(f"- **Cost:** ${tc.cost:.4f}")
                lines.append(f"- **Time:** {tc.time_taken:.2f}s")
                lines.append("")
                
                # Evaluator results
                lines.append("**Evaluator Results:**")
                for eval_result in tc.evaluation_results:
                    status = "✅" if eval_result.passed else "❌"
                    lines.append(f"- {status} {eval_result.evaluator_type}")
                    if eval_result.reason:
                        lines.append(f"  - {eval_result.reason}")
                lines.append("")
        
        # Write file
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✓ Markdown report saved to {self.output_path}")
    
    def cleanup(self):
        """No cleanup needed"""
        pass
```

## Registration Methods

### 1. Inline Registration (Python API)

Best for: Scripts, notebooks, quick prototyping

```python
from judge_llm import evaluate, register_reporter
from my_reporters import CSVReporter, SlackReporter

# Register custom reporters
register_reporter("csv", CSVReporter)
register_reporter("slack", SlackReporter)

# Use them
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[
        {"type": "csv", "output_path": "./results.csv"},
        {"type": "slack", "webhook_url": "https://hooks.slack.com/..."}
    ]
)
```

### 2. Config-Based Registration

Best for: One-off custom reporters, testing

```yaml
# test.yaml
reporters:
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    output_path: ./results.csv
    
  - type: custom
    module_path: ./reporters/slack_reporter.py
    class_name: SlackReporter
    webhook_url: ${SLACK_WEBHOOK_URL}
    channel: "#evals"
```

### 3. Default Config Registration (Recommended)

Best for: Reusable reporters across multiple configs

Register once in `.judge_llm.defaults.yaml`:
```yaml
reporters:
  # Register CSV reporter
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    register_as: csv
  
  # Register Slack reporter
  - type: custom
    module_path: ./reporters/slack_reporter.py
    class_name: SlackReporter
    register_as: slack
```

Use everywhere by name:
```yaml
# test1.yaml
reporters:
  - type: csv
    output_path: ./test1.csv

# test2.yaml  
reporters:
  - type: csv
    output_path: ./test2.csv
  - type: slack
    webhook_url: ${SLACK_WEBHOOK_URL}
```

## Best Practices

### 1. Error Handling

```python
class RobustReporter(BaseReporter):
    def generate_report(self, report: EvaluationReport):
        try:
            # Your reporting logic
            self._send_to_external_service(report)
        except Exception as e:
            print(f"⚠️  Reporter failed: {e}")
            # Optionally fallback to file
            self._save_to_fallback_file(report)
    
    def cleanup(self):
        try:
            # Cleanup logic
            self._close_connections()
        except Exception as e:
            print(f"⚠️  Cleanup failed: {e}")
```

### 2. Configuration Validation

```python
class ConfiguredReporter(BaseReporter):
    def __init__(self, config: dict = None):
        self.config = config or {}
        
        # Validate required config
        required = ["api_key", "endpoint"]
        missing = [k for k in required if k not in self.config]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        
        self.api_key = self.config["api_key"]
        self.endpoint = self.config["endpoint"]
```

### 3. Environment Variables

```python
import os

class SecureReporter(BaseReporter):
    def __init__(self, config: dict = None):
        self.config = config or {}
        
        # Support both config and env vars
        self.api_key = (
            self.config.get("api_key") or
            os.environ.get("REPORTER_API_KEY")
        )
        
        if not self.api_key:
            raise ValueError("API key required (config or REPORTER_API_KEY env var)")
```

### 4. Progress Feedback

```python
class VerboseReporter(BaseReporter):
    def generate_report(self, report: EvaluationReport):
        print(f"Generating report for {len(report.test_cases)} test cases...")
        
        # Do work
        self._process_results(report)
        
        print(f"✓ Report generated successfully")
```

### 5. Resource Cleanup

```python
class ResourceReporter(BaseReporter):
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.connection = None
    
    def generate_report(self, report: EvaluationReport):
        self.connection = self._connect()
        self._send_data(report)
        # Don't close here - use cleanup()
    
    def cleanup(self):
        """Always called after generate_report"""
        if self.connection:
            self.connection.close()
            self.connection = None
```

## Testing Custom Reporters

### Unit Test Example

```python
import pytest
from judge_llm.core.models import EvaluationReport, TestCaseResult
from my_reporters import CSVReporter
from pathlib import Path

def test_csv_reporter():
    # Create mock report
    report = EvaluationReport(
        total_cost=0.05,
        total_time=10.0,
        success_rate=0.8,
        overall_success=True,
        summary={
            "total_executions": 5,
            "successful_executions": 4,
            "failed_executions": 1
        },
        test_cases=[
            TestCaseResult(
                eval_id="test_1",
                agent_id="agent_1",
                provider_type="gemini",
                passed=True,
                cost=0.01,
                time_taken=2.0,
                evaluation_results=[],
                conversation_history=[]
            )
        ]
    )
    
    # Test reporter
    output_path = Path("/tmp/test_report.csv")
    reporter = CSVReporter({"output_path": str(output_path)})
    reporter.generate_report(report)
    
    # Verify output
    assert output_path.exists()
    content = output_path.read_text()
    assert "test_1" in content
    assert "agent_1" in content
    
    # Cleanup
    reporter.cleanup()
    output_path.unlink()
```

## Related Documentation

- [Reporters Overview](./overview.md)
- [Console Reporter](./console-reporter.md)
- [JSON Reporter](./json-reporter.md)
- [HTML Reporter](./html-reporter.md)
- [Database Reporter](./database-reporter.md)
- [Custom Evaluators](../evaluators/custom-evaluators.md)
