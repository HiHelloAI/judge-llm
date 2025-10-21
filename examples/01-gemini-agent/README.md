# Example 01: Basic Gemini Agent Evaluation

This example demonstrates the most basic usage of Judge LLM - evaluating a Gemini agent with response evaluation.

## What You'll Learn

- Basic evaluation setup
- Configuring a Gemini provider
- Using the response evaluator
- Running evaluations via CLI and Python API

## Files

- `config.yaml` - Basic configuration file
- `sample.evalset.json` - Sample test cases (JSON format)
- `sample.evalset.yaml` - Sample test cases (YAML format)
- `run.sh` - Shell script to run evaluation
- `run_evaluation.py` - Python script to run evaluation
- `README.md` - This file

## Prerequisites

1. Install Judge LLM:
```bash
pip install judge-llm
```

2. Set your Gemini API key:
```bash
export GEMINI_API_KEY=your_api_key_here
```

Or create a `.env` file:
```bash
echo "GEMINI_API_KEY=your_key" > .env
```

## Configuration

### config.yaml

```yaml
dataset:
  loader: local_file
  paths:
    - ./sample.evalset.json  # or ./sample.evalset.yaml

providers:
  - type: gemini
    agent_id: gemini_agent
    model: gemini-2.0-flash-exp
    temperature: 0.0

evaluators:
  - type: response_evaluator
    llm_provider: gemini

reporters:
  - type: console
```

This configuration:
- Loads test cases from `sample.evalset.json` (or `sample.evalset.yaml` - both formats supported)
- Uses Gemini Flash model with temperature 0 (deterministic)
- Evaluates responses using LLM-as-judge
- Outputs results to console

### sample.evalset.json

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
  }
]
```

Simple test cases with expected responses.

## Running the Example

### Method 1: CLI

```bash
cd examples/01-gemini-agent
judge-llm run --config config.yaml
```

### Method 2: Shell Script

```bash
./run.sh
```

### Method 3: Python API

```bash
python run_evaluation.py
```

## Expected Output

```
Starting evaluation...

Evaluation Progress:
  test_001: ✓ PASSED (cost: $0.0012, time: 1.2s)

Summary:
  Total Tests: 1
  Passed: 1
  Failed: 0
  Success Rate: 100.0%
  Total Cost: $0.0012
  Total Time: 1.2s
```

## Understanding the Results

- **Passed/Failed**: Whether the agent's response matched expectations
- **Cost**: API cost for this test case
- **Time**: Execution time
- **Success Rate**: Percentage of tests passed

## Troubleshooting

### API Key Not Found

**Error:** `API key not found for provider: gemini`

**Solution:** Set `GEMINI_API_KEY` environment variable or create `.env` file

### Test File Not Found

**Error:** `Test file not found: ./sample.evalset.json`

**Solution:** Ensure you're running from the example directory

## Next Steps

- Try modifying test cases in `sample.evalset.json`
- Experiment with different models
- Add more evaluators (cost, latency)
- Try different reporters (JSON, HTML)

## Related Examples

- [02-default-config](../02-default-config/) - Using default configuration
- [03-custom-evaluator](../03-custom-evaluator/) - Creating custom evaluators

## Related Documentation

- [Basic Usage Guide](../../docs/docs/guides/basic-usage.md)
- [Configuration Guide](../../docs/docs/guides/configuration.md)
- [CLI Reference](../../docs/docs/guides/cli-reference.md)
