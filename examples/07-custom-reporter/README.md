# Custom Reporter Example

This example demonstrates how to create and use custom reporters in Judge LLM.

## What's Included

- **custom_reporter.py** - A custom CSV reporter implementation
- **config_based.yaml** - Using custom reporter via YAML configuration
- **programmatic.py** - Three examples of programmatic reporter registration

## The Custom Reporter

`CSVReporter` outputs evaluation results to a CSV file with the following columns:
- eval_id
- agent_id
- provider_type
- passed
- cost
- latency_seconds
- evaluators_passed
- evaluators_total

## Usage Methods

### 1. Configuration-Based (YAML)

```yaml
reporters:
  - type: custom
    module_path: ./custom_reporter.py
    class_name: CSVReporter
    config:
      output_path: ./results.csv
```

Run:
```bash
judge-llm run --config config_based.yaml
```

### 2. Programmatic Registration

```python
from judge_llm import evaluate, register_reporter
from custom_reporter import CSVReporter

# Register globally
register_reporter("csv", CSVReporter)

# Use by name
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "mock", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[
        {"type": "csv", "config": {"output_path": "./report.csv"}}
    ],
)
```

### 3. Inline Usage (No Registration)

```python
from judge_llm import evaluate

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "mock", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[
        {
            "type": "custom",
            "module_path": "./custom_reporter.py",
            "class_name": "CSVReporter",
            "config": {"output_path": "./report.csv"}
        }
    ],
)
```

## Running the Examples

```bash
cd examples/custom_reporter_example

# Run programmatic examples
python programmatic.py

# Run config-based example
judge-llm run --config config_based.yaml
```

## Creating Your Own Reporter

1. **Inherit from BaseReporter:**

```python
from judge_llm.reporters.base import BaseReporter
from judge_llm.core.models import EvaluationReport

class MyReporter(BaseReporter):
    def __init__(self, config: dict = None):
        self.config = config or {}
        # Your initialization
    
    def generate_report(self, report: EvaluationReport):
        # Your report generation logic
        pass
    
    def cleanup(self):
        # Cleanup resources
        pass
```

2. **Register and use:**

```python
from judge_llm import register_reporter

register_reporter("my_reporter", MyReporter)
```

## Built-in Reporters

Judge LLM includes these built-in reporters:
- `console` - Terminal output
- `json` - JSON file
- `html` - Interactive HTML report
- `database` - SQLite database

Check available reporters:
```bash
judge-llm list reporters
```

## Benefits of Custom Reporters

- **Custom Formats**: CSV, Excel, Markdown, XML, etc.
- **Integrations**: Send results to monitoring systems, databases, APIs
- **Notifications**: Email, Slack, webhooks on evaluation completion
- **Dashboards**: Custom visualization and analytics
- **CI/CD**: Integration with testing pipelines

## Learn More

See the Judge LLM documentation for more details on creating custom reporters and the reporter API.
