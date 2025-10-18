---
sidebar_position: 3
---

# Quick Start

Get up and running with Judge LLM in 5 minutes.

## Step 1: Install Judge LLM

```bash
pip install -e .
```

## Step 2: Create Your First Eval Set

Create a file called `my_first_eval.json`:

```json
{
  "eval_set_id": "quick_start_eval",
  "name": "Quick Start Evaluation",
  "eval_cases": [
    {
      "eval_id": "test_001",
      "conversation": [
        {
          "invocation_id": "inv_001",
          "user_content": {
            "parts": [{"text": "What is 2+2?"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "The answer is 4."}],
            "role": "assistant"
          }
        }
      ],
      "session_input": {
        "app_name": "calculator",
        "user_id": "test_user",
        "user_prompt": "What is 2+2?"
      }
    }
  ]
}
```

## Step 3: Create a Configuration File

Create `config.yaml`:

```yaml
dataset:
  loader: local_file
  paths: [./my_first_eval.json]

providers:
  - type: mock
    agent_id: test_agent

evaluators:
  - type: response_evaluator
    config: {similarity_threshold: 0.8}

reporters:
  - type: console
  - type: html
    output_path: ./report.html
```

## Step 4: Run Your First Evaluation

```bash
judge-llm run --config config.yaml
```

You should see output like:

```
================================================================================
Evaluation Summary
================================================================================

Total executions: 1
Success rate: 100.0%
Total cost: $0.0000
Total time: 0.05s

✓ Evaluation completed successfully!
```

## Step 5: View the HTML Report

Open `report.html` in your browser to see an interactive dashboard with:

- Execution details
- Evaluator results
- Conversation history
- Cost and performance metrics

## What's Next?

- [Learn about Providers](./providers/overview.md) - Use real LLMs like Gemini
- [Explore Evaluators](./evaluators/overview.md) - Understand different evaluation metrics
- [View Examples](./examples/overview.md) - See complete example projects
- [Configuration Guide](./guides/configuration.md) - Learn all configuration options

## Quick Tips

### Using Real Providers

To use Google Gemini instead of mock:

```yaml
providers:
  - type: gemini
    agent_id: my_agent
    model: gemini-2.0-flash-exp
```

Don't forget to set `GOOGLE_API_KEY` in your `.env` file!

### Multiple Test Cases

Add more test cases to your eval set to thoroughly test your agent:

```json
{
  "eval_cases": [
    {"eval_id": "test_001", ...},
    {"eval_id": "test_002", ...},
    {"eval_id": "test_003", ...}
  ]
}
```

### Programmatic API

Prefer Python code? Use the programmatic API:

```python
from judge_llm import evaluate

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./my_first_eval.json"]},
    providers=[{"type": "mock", "agent_id": "test_agent"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "console"}]
)

print(f"Success rate: {report.success_rate:.1%}")
```
