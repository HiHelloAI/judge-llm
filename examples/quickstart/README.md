# Quickstart Example

This example demonstrates the basic usage of Judge LLM framework.

## Files

- `config.yaml` - Configuration file with all settings
- `sample.evalset.json` - Sample evaluation dataset
- `run.py` - Python script to run evaluation programmatically
- `run.sh` - Shell script to run evaluation via CLI

## Running the Example

### Option 1: Using Python Script

```bash
python run.py
```

### Option 2: Using CLI

```bash
./run.sh
```

Or directly:

```bash
judge-llm run --config config.yaml
```

## What This Example Does

1. Loads the sample eval set from `sample.evalset.json`
2. Uses the MockProvider to execute each eval case
3. Runs all built-in evaluators:
   - Response Validator (checks response similarity)
   - Trajectory Validator (validates tool usage)
   - Cost Evaluator (checks cost is within threshold)
   - Latency Evaluator (checks execution time)
4. Generates reports:
   - Console output (terminal)
   - JSON file (`report.json`)

## Expected Output

You should see:
- Summary statistics (success rate, cost, time)
- Execution details for each eval case
- Evaluator results showing pass/fail status
- Generated report files

## Configuration

The `config.yaml` file contains all configuration options:
- Agent settings (num_runs, parallel execution, etc.)
- Dataset paths
- Provider configuration
- Evaluator settings with thresholds
- Reporter types and output paths

Feel free to modify the configuration to experiment with different settings!
