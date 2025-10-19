---
sidebar_position: 2
---

# Python API Reference

Complete Python API reference for programmatic evaluation and custom integrations.

## Core Functions

### evaluate()

The main entry point for running evaluations programmatically.

```python
from judge_llm import evaluate

report = evaluate(
    dataset: dict,
    providers: list[dict],
    evaluators: list[dict],
    reporters: list[dict] = None,
    validate: bool = True
) -> EvaluationReport
```

**Parameters:**

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `dataset` | `dict` | Dataset loader configuration | Yes |
| `providers` | `list[dict]` | List of provider configurations | Yes |
| `evaluators` | `list[dict]` | List of evaluator configurations | Yes |
| `reporters` | `list[dict]` | List of reporter configurations | No |
| `validate` | `bool` | Whether to validate config (default: True) | No |

**Returns:** `EvaluationReport` object containing all results

**Example:**

```python
from judge_llm import evaluate

report = evaluate(
    dataset={
        "loader": "local_file",
        "paths": ["./tests.json"]
    },
    providers=[
        {"type": "gemini", "agent_id": "test_agent"}
    ],
    evaluators=[
        {"type": "response_evaluator"}
    ],
    reporters=[
        {"type": "console"},
        {"type": "json", "output_path": "./results.json"}
    ]
)

# Access results
print(f"Success rate: {report.success_rate * 100:.1f}%")
print(f"Total cost: ${report.total_cost:.4f}")
print(f"Passed: {report.summary['successful_executions']}/{report.summary['total_executions']}")
```

## Registration Functions

### register_provider()

Register a custom provider class.

```python
from judge_llm import register_provider

register_provider(name: str, provider_class: Type[BaseProvider])
```

**Example:**

```python
from judge_llm import register_provider
from judge_llm.providers.base import BaseProvider

class MyCustomProvider(BaseProvider):
    def initialize(self):
        # Setup
        pass
    
    def execute(self, conversation_history):
        # Execute and return response
        return {"content": "response"}

# Register
register_provider("my_provider", MyCustomProvider)

# Use
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "my_provider", "agent_id": "custom"}],
    evaluators=[{"type": "response_evaluator"}]
)
```

### register_evaluator()

Register a custom evaluator class.

```python
from judge_llm import register_evaluator

register_evaluator(name: str, evaluator_class: Type[BaseEvaluator])
```

**Example:**

```python
from judge_llm import register_evaluator
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvaluationResult

class SafetyEvaluator(BaseEvaluator):
    def evaluate(self, test_case, response):
        # Check for unsafe content
        unsafe_terms = ["violence", "harmful"]
        content = response.get("content", "").lower()
        
        is_safe = not any(term in content for term in unsafe_terms)
        
        return EvaluationResult(
            evaluator_type="safety",
            passed=is_safe,
            score=1.0 if is_safe else 0.0,
            reason="Safe content" if is_safe else "Unsafe content detected"
        )

# Register
register_evaluator("safety", SafetyEvaluator)

# Use
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[
        {"type": "response_evaluator"},
        {"type": "safety"}  # Your custom evaluator
    ]
)
```

### register_reporter()

Register a custom reporter class.

```python
from judge_llm import register_reporter

register_reporter(name: str, reporter_class: Type[BaseReporter])
```

**Example:**

```python
from judge_llm import register_reporter
from judge_llm.reporters.base import BaseReporter
import csv

class CSVReporter(BaseReporter):
    def __init__(self, config=None):
        self.config = config or {}
        self.output_path = self.config.get("output_path", "./results.csv")
    
    def generate_report(self, report):
        with open(self.output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['eval_id', 'passed', 'cost', 'time'])
            for tc in report.test_cases:
                writer.writerow([tc.eval_id, tc.passed, tc.cost, tc.time_taken])
    
    def cleanup(self):
        pass

# Register
register_reporter("csv", CSVReporter)

# Use
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "csv", "output_path": "./results.csv"}]
)
```

## Data Models

### EvaluationReport

The complete evaluation report returned by `evaluate()`.

```python
@dataclass
class EvaluationReport:
    total_cost: float                    # Total cost across all tests
    total_time: float                    # Total execution time (seconds)
    success_rate: float                  # Percentage of passed tests (0-1)
    overall_success: bool                # True if all tests passed
    summary: Dict[str, Any]              # Aggregated statistics
    test_cases: List[TestCaseResult]     # Individual test results
```

**Example:**

```python
report = evaluate(...)

# Access summary stats
print(f"Total cost: ${report.total_cost:.4f}")
print(f"Success rate: {report.success_rate * 100:.1f}%")
print(f"Total tests: {report.summary['total_executions']}")
print(f"Passed: {report.summary['successful_executions']}")
print(f"Failed: {report.summary['failed_executions']}")

# Iterate test cases
for tc in report.test_cases:
    if not tc.passed:
        print(f"Failed: {tc.eval_id}")
```

### TestCaseResult

Individual test case result.

```python
@dataclass
class TestCaseResult:
    eval_id: str                                # Test case ID
    agent_id: str                               # Agent identifier
    provider_type: str                          # Provider type
    passed: bool                                # Overall pass/fail
    cost: float                                 # Cost for this test
    time_taken: float                           # Execution time (seconds)
    evaluation_results: List[EvaluationResult]  # Evaluator results
    conversation_history: List[Dict[str, Any]]  # Full conversation
```

**Example:**

```python
report = evaluate(...)

for tc in report.test_cases:
    print(f"\nTest: {tc.eval_id}")
    print(f"  Status: {'✅ PASSED' if tc.passed else '❌ FAILED'}")
    print(f"  Cost: ${tc.cost:.4f}")
    print(f"  Time: {tc.time_taken:.2f}s")
    
    # Check individual evaluators
    for eval_result in tc.evaluation_results:
        status = "✅" if eval_result.passed else "❌"
        print(f"  {status} {eval_result.evaluator_type}: {eval_result.reason}")
```

### EvaluationResult

Result from a single evaluator.

```python
@dataclass
class EvaluationResult:
    evaluator_type: str      # Evaluator name
    passed: bool             # Pass/fail
    score: float            # Numeric score (0-1)
    reason: str             # Explanation
    metadata: dict          # Additional info
```

**Example:**

```python
report = evaluate(...)

for tc in report.test_cases:
    for eval_result in tc.evaluation_results:
        if not eval_result.passed:
            print(f"Evaluator {eval_result.evaluator_type} failed:")
            print(f"  Reason: {eval_result.reason}")
            print(f"  Score: {eval_result.score}")
            if eval_result.metadata:
                print(f"  Metadata: {eval_result.metadata}")
```

## Configuration from Code

### Dataset Configuration

```python
# Local file
dataset = {
    "loader": "local_file",
    "paths": ["./tests.json", "./more_tests.json"]
}

# BrowserBase (for web data)
dataset = {
    "loader": "browserbase",
    "api_key": "your_api_key",
    "project_id": "your_project_id"
}
```

### Provider Configuration

```python
# Gemini
providers = [{
    "type": "gemini",
    "agent_id": "gemini_agent",
    "model": "gemini-2.0-flash-exp",
    "temperature": 0.0,
    "api_key": "your_api_key"  # Or use env var
}]

# OpenAI
providers = [{
    "type": "openai",
    "agent_id": "openai_agent",
    "model": "gpt-4",
    "temperature": 0.7,
    "api_key": "your_api_key"
}]

# Anthropic
providers = [{
    "type": "anthropic",
    "agent_id": "claude_agent",
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.0,
    "api_key": "your_api_key"
}]

# Multiple providers (A/B testing)
providers = [
    {"type": "gemini", "agent_id": "gemini"},
    {"type": "openai", "agent_id": "openai"},
    {"type": "anthropic", "agent_id": "claude"}
]
```

### Evaluator Configuration

```python
# Response evaluator
evaluators = [{
    "type": "response_evaluator",
    "llm_provider": "gemini",
    "llm_model": "gemini-2.0-flash-exp"
}]

# Trajectory evaluator
evaluators = [{
    "type": "trajectory_evaluator",
    "llm_provider": "gemini"
}]

# Cost evaluator
evaluators = [{
    "type": "cost_evaluator",
    "max_cost": 0.01  # Fail if cost > $0.01
}]

# Latency evaluator
evaluators = [{
    "type": "latency_evaluator",
    "max_latency": 5.0  # Fail if latency > 5s
}]

# Multiple evaluators
evaluators = [
    {"type": "response_evaluator"},
    {"type": "cost_evaluator", "max_cost": 0.01},
    {"type": "latency_evaluator", "max_latency": 3.0}
]
```

### Reporter Configuration

```python
# Console reporter
reporters = [{"type": "console"}]

# JSON reporter
reporters = [{
    "type": "json",
    "output_path": "./results.json"
}]

# HTML reporter
reporters = [{
    "type": "html",
    "output_path": "./report.html"
}]

# Database reporter
reporters = [{
    "type": "database",
    "db_path": "./results.db"
}]

# Multiple reporters
reporters = [
    {"type": "console"},
    {"type": "json", "output_path": "./results.json"},
    {"type": "html", "output_path": "./report.html"},
    {"type": "database", "db_path": "./results.db"}
]
```

## Advanced Usage

### Environment Variables

```python
import os
from dotenv import load_dotenv
from judge_llm import evaluate

# Load .env file
load_dotenv()

report = evaluate(
    dataset={
        "loader": "local_file",
        "paths": [os.getenv("TEST_FILE_PATH")]
    },
    providers=[{
        "type": "gemini",
        "agent_id": os.getenv("AGENT_ID"),
        "api_key": os.getenv("GEMINI_API_KEY")
    }],
    evaluators=[{"type": "response_evaluator"}]
)
```

### Error Handling

```python
from judge_llm import evaluate

try:
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["./tests.json"]},
        providers=[{"type": "gemini", "agent_id": "test"}],
        evaluators=[{"type": "response_evaluator"}]
    )
    
    if report.overall_success:
        print("✅ All tests passed!")
    else:
        print(f"❌ {report.summary['failed_executions']} tests failed")
        
        # Print failed tests
        for tc in report.test_cases:
            if not tc.passed:
                print(f"  - {tc.eval_id}")
                
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Evaluation failed: {e}")
```

### Conditional Evaluation

```python
from judge_llm import evaluate

def run_evaluation(config_name: str):
    """Run evaluation and return pass/fail"""
    report = evaluate(
        dataset={"loader": "local_file", "paths": [f"./{config_name}.json"]},
        providers=[{"type": "gemini", "agent_id": config_name}],
        evaluators=[{"type": "response_evaluator"}],
        reporters=[{"type": "json", "output_path": f"./{config_name}_results.json"}]
    )
    return report.overall_success

# Run multiple evaluations
configs = ["dev", "staging", "prod"]
results = {config: run_evaluation(config) for config in configs}

# Check if all passed
if all(results.values()):
    print("✅ All environments passed!")
else:
    failed = [k for k, v in results.items() if not v]
    print(f"❌ Failed environments: {', '.join(failed)}")
```

### Custom Analysis

```python
from judge_llm import evaluate
import pandas as pd

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[
        {"type": "gemini", "agent_id": "gemini"},
        {"type": "openai", "agent_id": "openai"}
    ],
    evaluators=[{"type": "response_evaluator"}]
)

# Convert to DataFrame for analysis
data = []
for tc in report.test_cases:
    data.append({
        'eval_id': tc.eval_id,
        'provider': tc.provider_type,
        'passed': tc.passed,
        'cost': tc.cost,
        'latency': tc.time_taken
    })

df = pd.DataFrame(data)

# Analysis
print("\nCost by Provider:")
print(df.groupby('provider')['cost'].agg(['mean', 'sum', 'count']))

print("\nLatency by Provider:")
print(df.groupby('provider')['latency'].agg(['mean', 'min', 'max']))

print("\nSuccess Rate by Provider:")
print(df.groupby('provider')['passed'].mean() * 100)
```

### Integration with Testing Frameworks

#### pytest

```python
# test_llm_eval.py
import pytest
from judge_llm import evaluate

def test_llm_evaluation():
    """Test that LLM passes all evaluations"""
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["./tests.json"]},
        providers=[{"type": "gemini", "agent_id": "test"}],
        evaluators=[{"type": "response_evaluator"}]
    )
    
    assert report.overall_success, f"Evaluation failed: {report.summary['failed_executions']} tests failed"
    assert report.success_rate >= 0.9, f"Success rate too low: {report.success_rate * 100:.1f}%"
    assert report.total_cost < 1.0, f"Cost too high: ${report.total_cost:.2f}"

def test_individual_test_cases():
    """Test specific test cases"""
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["./tests.json"]},
        providers=[{"type": "gemini", "agent_id": "test"}],
        evaluators=[{"type": "response_evaluator"}]
    )
    
    # Check specific test
    test_001 = next(tc for tc in report.test_cases if tc.eval_id == "test_001")
    assert test_001.passed, "test_001 should pass"
```

#### unittest

```python
# test_llm_eval.py
import unittest
from judge_llm import evaluate

class TestLLMEvaluation(unittest.TestCase):
    def test_overall_success(self):
        """Test that all evaluations pass"""
        report = evaluate(
            dataset={"loader": "local_file", "paths": ["./tests.json"]},
            providers=[{"type": "gemini", "agent_id": "test"}],
            evaluators=[{"type": "response_evaluator"}]
        )
        
        self.assertTrue(report.overall_success)
        self.assertGreaterEqual(report.success_rate, 0.9)
    
    def test_cost_threshold(self):
        """Test that cost is within threshold"""
        report = evaluate(
            dataset={"loader": "local_file", "paths": ["./tests.json"]},
            providers=[{"type": "gemini", "agent_id": "test"}],
            evaluators=[{"type": "cost_evaluator", "max_cost": 0.01}]
        )
        
        self.assertLess(report.total_cost, 1.0)

if __name__ == '__main__':
    unittest.main()
```

## Related Documentation

- [CLI Reference](./cli-reference.md)
- [Configuration Guide](./configuration.md)
- [Custom Evaluators](../evaluators/custom-evaluators.md)
- [Custom Reporters](../reporters/custom-reporters.md)
