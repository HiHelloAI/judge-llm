---
sidebar_position: 4
---

# JSON Reporter

Export evaluation results as structured JSON for programmatic analysis, data pipelines, and tool integration.

## Overview

The **JSON Reporter** outputs evaluation results as a structured JSON file. Perfect for automation, data analysis, and integration with other tools.

**Key Features:**
- Machine-readable structured format
- Complete evaluation data export
- Easy to parse and process
- Version control friendly
- Schema-consistent output

## Configuration

### Basic Configuration

```yaml
reporters:
  - type: json
    output_path: ./results.json
```

### Python API

```python
from judge_llm import evaluate

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "json", "output_path": "./results.json"}]
)
```

## Output Format

### Top-Level Structure

```json
{
  "total_cost": 0.0234,
  "total_time": 12.45,
  "success_rate": 0.85,
  "overall_success": true,
  "summary": {
    "total_executions": 10,
    "successful_executions": 8,
    "failed_executions": 2
  },
  "test_cases": [...]
}
```

### Test Case Structure

```json
{
  "eval_id": "test_001",
  "agent_id": "my_agent",
  "provider_type": "gemini",
  "passed": true,
  "cost": 0.00234,
  "time_taken": 1.234,
  "evaluation_results": [...],
  "conversation_history": [...]
}
```

## Use Cases

### Programmatic Analysis

```python
import json

# Load results
with open("results.json") as f:
    data = json.load(f)

# Analyze pass rate
print(f"Success rate: {data['success_rate'] * 100:.1f}%")

# Find expensive tests
expensive = [
    tc for tc in data['test_cases'] 
    if tc['cost'] > 0.01
]
print(f"Expensive tests: {len(expensive)}")

# Calculate average latency
avg_latency = sum(tc['time_taken'] for tc in data['test_cases']) / len(data['test_cases'])
print(f"Average latency: {avg_latency:.2f}s")
```

### CI/CD Integration

```yaml
# .github/workflows/eval.yml
- name: Run Evaluations
  run: judge-llm run --config test.yaml --report json --output results.json

- name: Analyze Results
  run: python analyze_results.py results.json

- name: Fail if Low Pass Rate
  run: |
    pass_rate=$(jq '.success_rate' results.json)
    if (( $(echo "$pass_rate < 0.9" | bc -l) )); then
      echo "Pass rate too low: $pass_rate"
      exit 1
    fi
```

### Data Pipelines

```python
# ETL pipeline
import json
import pandas as pd

# Load JSON results
with open("results.json") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data['test_cases'])

# Analyze
print(df.groupby('provider_type')['cost'].sum())
print(df[['eval_id', 'passed', 'time_taken']])

# Export to CSV
df.to_csv("analysis.csv", index=False)
```

### Version Control

```bash
# Track results over time
git add results.json
git commit -m "Evaluation results for v2.0"

# Compare with previous
git diff HEAD~1 results.json
```

## Best Practices

### 1. Timestamped Outputs

```yaml
reporters:
  - type: json
    output_path: ./results/eval-{{timestamp}}.json
```

### 2. Combine with Other Reporters

```yaml
reporters:
  - type: console    # Monitor progress
  - type: json       # Export for analysis
    output_path: ./results.json
```

### 3. Structured Storage

```
results/
  ├── 2025-01-15/
  │   ├── morning-eval.json
  │   └── afternoon-eval.json
  └── 2025-01-16/
      └── daily-eval.json
```

### 4. Schema Validation

```python
import json
import jsonschema

# Define expected schema
schema = {
    "type": "object",
    "required": ["total_cost", "success_rate", "test_cases"],
    "properties": {
        "success_rate": {"type": "number", "minimum": 0, "maximum": 1}
    }
}

# Validate
with open("results.json") as f:
    data = json.load(f)
jsonschema.validate(data, schema)
```

## Related Documentation

- [Reporters Overview](./overview.md)
- [Console Reporter](./console-reporter.md)
- [HTML Reporter](./html-reporter.md)
- [Database Reporter](./database-reporter.md)
