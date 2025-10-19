---
sidebar_position: 4
---

# Basic Usage

Get started with Judge LLM quickly - from installation to your first evaluation in minutes.

## Installation

Install Judge LLM using pip:

```bash
pip install judge-llm
```

Verify installation:

```bash
judge-llm --version
```

## Quick Start

### 1. Set Up API Keys

Create a `.env` file in your project root:

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Or set environment variables:

```bash
export GEMINI_API_KEY=your_key
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
```

### 2. Create Test Cases

Create a `tests.json` file with your test cases:

```json
[
  {
    "eval_id": "test_001",
    "turns": [
      {
        "role": "user",
        "content": "What is 2+2?"
      },
      {
        "role": "assistant",
        "content": "4",
        "expected": true
      }
    ]
  },
  {
    "eval_id": "test_002",
    "turns": [
      {
        "role": "user",
        "content": "What is the capital of France?"
      },
      {
        "role": "assistant",
        "content": "Paris",
        "expected": true
      }
    ]
  }
]
```

### 3. Create Configuration

Create a `test.yaml` configuration file:

```yaml
dataset:
  loader: local_file
  paths:
    - ./tests.json

providers:
  - type: gemini
    agent_id: my_agent

evaluators:
  - type: response_evaluator

reporters:
  - type: console
```

### 4. Run Evaluation

```bash
judge-llm run --config test.yaml
```

**Output:**

```
Starting evaluation...

Evaluation Progress:
  test_001: ✓ PASSED (cost: $0.0012, time: 1.2s)
  test_002: ✓ PASSED (cost: $0.0015, time: 1.5s)

Summary:
  Total Tests: 2
  Passed: 2
  Failed: 0
  Success Rate: 100.0%
  Total Cost: $0.0027
  Total Time: 2.7s
```

## Using Python API

You can also run evaluations programmatically:

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
print(f"Tests Passed: {report.summary['successful_executions']}")
```

## Common Usage Patterns

### Single Provider Evaluation

Test one model:

```yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini
    agent_id: gemini_agent

evaluators:
  - type: response_evaluator

reporters:
  - type: console
```

```bash
judge-llm run --config test.yaml
```

### Multiple Providers (A/B Testing)

Compare multiple models:

```yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini
    agent_id: gemini
  - type: openai
    agent_id: openai

evaluators:
  - type: response_evaluator

reporters:
  - type: console
  - type: html
    output_path: ./comparison.html
```

### Multiple Evaluators

Use multiple evaluation criteria:

```yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini
    agent_id: test_agent

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.01
  - type: latency_evaluator
    max_latency: 3.0

reporters:
  - type: console
```

### Multiple Output Formats

Generate multiple report types:

```yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini
    agent_id: test_agent

evaluators:
  - type: response_evaluator

reporters:
  - type: console
  - type: json
    output_path: ./results.json
  - type: html
    output_path: ./report.html
  - type: database
    db_path: ./results.db
```

## Test Case Format

### Single Turn

```json
{
  "eval_id": "simple_test",
  "turns": [
    {
      "role": "user",
      "content": "What is 2+2?"
    },
    {
      "role": "assistant",
      "content": "4",
      "expected": true
    }
  ]
}
```

### Multi-Turn Conversation

```json
{
  "eval_id": "conversation_test",
  "turns": [
    {
      "role": "user",
      "content": "What is 2+2?"
    },
    {
      "role": "assistant",
      "content": "4",
      "expected": true
    },
    {
      "role": "user",
      "content": "And what is 4+4?"
    },
    {
      "role": "assistant",
      "content": "8",
      "expected": true
    }
  ]
}
```

### With System Prompt

```json
{
  "eval_id": "system_prompt_test",
  "turns": [
    {
      "role": "system",
      "content": "You are a helpful math tutor."
    },
    {
      "role": "user",
      "content": "What is 2+2?"
    },
    {
      "role": "assistant",
      "content": "4",
      "expected": true
    }
  ]
}
```

## Best Practices

### 1. Start Simple

Begin with a few test cases and one provider:

```yaml
dataset:
  loader: local_file
  paths: [./tests.json]  # Start with 5-10 tests

providers:
  - type: gemini
    agent_id: test

evaluators:
  - type: response_evaluator

reporters:
  - type: console
```

### 2. Use Environment Variables

Never commit API keys:

```yaml
# Good
providers:
  - type: gemini
    api_key: ${GEMINI_API_KEY}

# Bad
providers:
  - type: gemini
    api_key: "AIzaSy..."  # Don't do this!
```

### 3. Iterate Incrementally

1. Start with basic response evaluation
2. Add cost/latency checks
3. Add custom evaluators
4. Expand test coverage

### 4. Version Control Your Tests

```bash
git add tests.json test.yaml
git commit -m "Add test cases for feature X"
```

### 5. Monitor Costs

Add cost evaluator to prevent surprises:

```yaml
evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.01  # Fail if cost > $0.01 per test
```

## Common Mistakes

### Missing API Keys

**Error:** `API key not found for provider: gemini`

**Solution:** Set environment variable or create `.env` file

### Invalid Test Format

**Error:** `Invalid test case format`

**Solution:** Ensure each test has `eval_id` and `turns` fields

### File Not Found

**Error:** `Test file not found: ./tests.json`

**Solution:** Check file path is correct relative to config file

### Wrong Provider Type

**Error:** `Unknown provider type: gpt`

**Solution:** Use correct provider names: `gemini`, `openai`, `anthropic`

## Getting Help

### List Available Components

```bash
# List providers
judge-llm list providers

# List evaluators
judge-llm list evaluators

# List reporters
judge-llm list reporters
```

### Validate Configuration

```bash
judge-llm validate --config test.yaml
```

### View Documentation

```bash
judge-llm --help
judge-llm run --help
```

## Next Steps

- [Configuration Guide](./configuration) - Learn all configuration options
- [CLI Reference](./cli-reference) - Complete CLI documentation
- [Python API](./python-api) - Programmatic usage
- [Examples](../examples) - Working examples for common scenarios
- [Custom Evaluators](../evaluators/custom-evaluators) - Build custom evaluators
- [Custom Reporters](../reporters/custom-reporters) - Build custom reporters

## Related Documentation

- [CLI Reference](./cli-reference)
- [Python API Reference](./python-api)
- [Configuration Guide](./configuration)
- [Examples](../examples)
