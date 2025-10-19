---
sidebar_position: 3
---

# Using the Python API

Run evaluations programmatically using the Python API for integration into your applications and workflows.

## Basic Usage

Instead of using YAML config files, you can run evaluations directly from Python:

```python
from judge_llm import evaluate

report = evaluate(
    dataset={
        "loader": "local_file",
        "paths": ["./tests.json"]
    },
    providers=[
        {"type": "gemini", "agent_id": "my_agent"}
    ],
    evaluators=[
        {"type": "response_evaluator"}
    ],
    reporters=[
        {"type": "console"}
    ]
)

# Access results
print(f"Success Rate: {report.success_rate * 100:.1f}%")
print(f"Total Cost: ${report.total_cost:.4f}")
print(f"Tests Passed: {report.summary['successful_executions']}/{report.summary['total_executions']}")
```

## Accessing Results

The `evaluate()` function returns an `EvaluationReport` object with all results:

```python
report = evaluate(...)

# Summary statistics
print(f"Total Cost: ${report.total_cost:.4f}")
print(f"Total Time: {report.total_time:.2f}s")
print(f"Success Rate: {report.success_rate * 100:.1f}%")
print(f"Overall Success: {report.overall_success}")

# Detailed summary
print(f"Total Tests: {report.summary['total_executions']}")
print(f"Passed: {report.summary['successful_executions']}")
print(f"Failed: {report.summary['failed_executions']}")

# Individual test cases
for test_case in report.test_cases:
    print(f"\nTest: {test_case.eval_id}")
    print(f"  Status: {'✅ PASSED' if test_case.passed else '❌ FAILED'}")
    print(f"  Cost: ${test_case.cost:.4f}")
    print(f"  Time: {test_case.time_taken:.2f}s")
    
    # Evaluator results
    for eval_result in test_case.evaluation_results:
        status = "✅" if eval_result.passed else "❌"
        print(f"  {status} {eval_result.evaluator_type}: {eval_result.reason}")
```

## Loading from Environment

Use environment variables for sensitive data:

```python
import os
from dotenv import load_dotenv
from judge_llm import evaluate

# Load .env file
load_dotenv()

report = evaluate(
    dataset={
        "loader": "local_file",
        "paths": [os.getenv("TEST_FILE", "./tests.json")]
    },
    providers=[{
        "type": "gemini",
        "agent_id": os.getenv("AGENT_ID", "default"),
        "api_key": os.getenv("GEMINI_API_KEY")
    }],
    evaluators=[{"type": "response_evaluator"}]
)
```

## Multiple Providers

Compare different models programmatically:

```python
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[
        {"type": "gemini", "agent_id": "gemini_flash"},
        {"type": "openai", "agent_id": "gpt4"},
        {"type": "anthropic", "agent_id": "claude"}
    ],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[
        {"type": "console"},
        {"type": "html", "output_path": "./comparison.html"}
    ]
)

# Analyze by provider
import pandas as pd

data = [{
    "provider": tc.provider_type,
    "passed": tc.passed,
    "cost": tc.cost,
    "latency": tc.time_taken
} for tc in report.test_cases]

df = pd.DataFrame(data)

print("\nResults by Provider:")
print(df.groupby("provider").agg({
    "passed": "mean",
    "cost": ["mean", "sum"],
    "latency": "mean"
}))
```

## Error Handling

Handle errors gracefully:

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
                for eval_result in tc.evaluation_results:
                    if not eval_result.passed:
                        print(f"    ✗ {eval_result.evaluator_type}: {eval_result.reason}")
    
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Evaluation failed: {e}")
```

## Custom Reporters

Generate custom output formats:

```python
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}]
)

# Save to CSV manually
import csv

with open("results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["eval_id", "passed", "cost", "time"])
    
    for tc in report.test_cases:
        writer.writerow([
            tc.eval_id,
            tc.passed,
            tc.cost,
            tc.time_taken
        ])

print("Results saved to results.csv")
```

## Conditional Evaluation

Run different evaluations based on conditions:

```python
import os
from judge_llm import evaluate

environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    # Stricter evaluation for production
    evaluators = [
        {"type": "response_evaluator"},
        {"type": "trajectory_evaluator"},
        {"type": "cost_evaluator", "max_cost": 0.01},
        {"type": "latency_evaluator", "max_latency": 3.0}
    ]
else:
    # Lenient for development
    evaluators = [
        {"type": "response_evaluator"}
    ]

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": f"{environment}_agent"}],
    evaluators=evaluators
)
```

## Integration with Testing Frameworks

### pytest

```python
# test_llm.py
import pytest
from judge_llm import evaluate

def test_llm_evaluation():
    """Test that LLM passes all evaluations"""
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["./tests.json"]},
        providers=[{"type": "gemini", "agent_id": "test"}],
        evaluators=[{"type": "response_evaluator"}]
    )
    
    assert report.overall_success, f"{report.summary['failed_executions']} tests failed"
    assert report.success_rate >= 0.9, f"Success rate too low: {report.success_rate:.1%}"

def test_cost_within_budget():
    """Test that evaluation stays within budget"""
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["./tests.json"]},
        providers=[{"type": "gemini", "agent_id": "test"}],
        evaluators=[{"type": "cost_evaluator", "max_cost": 0.01}]
    )
    
    assert report.total_cost < 1.0, f"Total cost too high: ${report.total_cost:.2f}"
```

Run with pytest:
```bash
pytest test_llm.py -v
```

### unittest

```python
# test_llm.py
import unittest
from judge_llm import evaluate

class TestLLMEvaluation(unittest.TestCase):
    
    def test_all_pass(self):
        """Test that all evaluations pass"""
        report = evaluate(
            dataset={"loader": "local_file", "paths": ["./tests.json"]},
            providers=[{"type": "gemini", "agent_id": "test"}],
            evaluators=[{"type": "response_evaluator"}]
        )
        
        self.assertTrue(report.overall_success)
        self.assertGreaterEqual(report.success_rate, 0.9)
    
    def test_specific_case(self):
        """Test specific test case"""
        report = evaluate(
            dataset={"loader": "local_file", "paths": ["./tests.json"]},
            providers=[{"type": "gemini", "agent_id": "test"}],
            evaluators=[{"type": "response_evaluator"}]
        )
        
        # Find specific test
        test_001 = next(tc for tc in report.test_cases if tc.eval_id == "test_001")
        self.assertTrue(test_001.passed, "test_001 should pass")

if __name__ == '__main__':
    unittest.main()
```

## Registering Custom Components

Register custom components for reuse:

```python
from judge_llm import evaluate, register_evaluator
from my_evaluators import SafetyEvaluator

# Register once
register_evaluator("safety", SafetyEvaluator)

# Use by name in multiple evaluations
report1 = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests1.json"]},
    providers=[{"type": "gemini", "agent_id": "test1"}],
    evaluators=[{"type": "safety"}]  # Use registered name
)

report2 = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests2.json"]},
    providers=[{"type": "gemini", "agent_id": "test2"}],
    evaluators=[{"type": "safety"}]  # Use registered name
)
```

## Next Steps

- [Configuration Guide](../guides/configuration) - Learn all configuration options
- [Python API Reference](../guides/python-api) - Complete API documentation
- [Custom Evaluators](../evaluators/custom-evaluators) - Build custom evaluators
- [Examples](../examples) - See more examples

## Related Documentation

- [CLI Reference](../guides/cli-reference) - Command-line usage
- [Basic Usage](../guides/basic-usage) - Quick start guide
- [Custom Reporters](../reporters/custom-reporters) - Build custom reporters
