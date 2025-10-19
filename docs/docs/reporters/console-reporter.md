---
sidebar_position: 2
---

# Console Reporter

Real-time terminal output with rich formatting and colored status indicators for monitoring evaluation progress.

## Overview

The **Console Reporter** displays evaluation results directly in your terminal using rich formatting, tables, and color-coded status. Perfect for development, debugging, and real-time monitoring.

**Key Features:**
- Live progress updates during execution
- Colored pass/fail indicators (green ✓, red ✗)
- Summary statistics (success rate, costs, latency)
- Detailed test case breakdowns
- Per-evaluator results with scores

## Configuration

### Basic Usage

```yaml
reporters:
  - type: console
```

That's it! No configuration needed.

### CLI Usage

```bash
# Console is the default reporter
judge-llm run --config test.yaml

# Explicitly specify console
judge-llm run --config test.yaml --report console
```

### Python API

```python
from judge_llm import evaluate

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "console"}]
)
```

## Output Format

### Execution Summary

```
================================================================================
  EVALUATION CONFIGURATION
================================================================================
┌──────────────────────────────────────────────────────────────────────────┐
│ Agent ID / Provider    │ Type    │ Runs │ Parallel │ Datasets   │ ...   │
├──────────────────────────────────────────────────────────────────────────┤
│ my_agent              │ gemini  │  1   │ No       │ tests.json │ ...   │
└──────────────────────────────────────────────────────────────────────────┘
================================================================================

▶ Starting evaluation...
```

### Test Results

```
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Eval ID    ┃ Provider ┃ Status  ┃ Cost   ┃ Latency   ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ test_001   │ gemini   │ ✓ PASS  │ $0.001 │ 1.23s     │
│ test_002   │ gemini   │ ✗ FAIL  │ $0.002 │ 2.45s     │
│ test_003   │ gemini   │ ✓ PASS  │ $0.001 │ 1.56s     │
└────────────┴──────────┴─────────┴────────┴───────────┘

Overall: 2/3 passed (66.7%)
Total Cost: $0.004
Total Time: 5.24s
```

### Per-Evaluator Results

```
Evaluator: ResponseEvaluator
  test_001: ✓ PASS (score: 0.92 / threshold: 0.80)
  test_002: ✗ FAIL (score: 0.65 / threshold: 0.80)
  test_003: ✓ PASS (score: 0.88 / threshold: 0.80)

Evaluator: CostEvaluator
  test_001: ✓ PASS ($0.001 / max: $0.010)
  test_002: ✓ PASS ($0.002 / max: $0.010)
  test_003: ✓ PASS ($0.001 / max: $0.010)
```

## Use Cases

### Development & Debugging

```bash
# Quick feedback loop
judge-llm run --config dev.yaml

# Watch progress in real-time
# See failures immediately
# Debug test cases interactively
```

### CI/CD Logs

```yaml
# .github/workflows/eval.yml
- name: Run LLM Evaluations
  run: judge-llm run --config ci.yaml --report console
```

Console output appears in GitHub Actions logs with proper formatting.

### Local Testing

```python
# Quick validation before committing
from judge_llm import evaluate

report = evaluate(
    config="./my-test.yaml",
    reporters=[{"type": "console"}]
)

if not report.overall_success:
    print("❌ Tests failed! Fix before committing.")
    exit(1)
```

## Features

### Color Coding

- **✓ Green** - Test passed
- **✗ Red** - Test failed
- **Yellow** - Warnings
- **Cyan** - Info/headers
- **Dim** - Secondary information

### Progress Indicators

Real-time progress as tests execute:
```
▶ Starting evaluation...
  [1/10] test_001 ✓
  [2/10] test_002 ✗
  [3/10] test_003 ✓
  ...
```

### Summary Statistics

Quick overview at the end:
- Success rate percentage
- Total cost across all tests
- Total execution time
- Pass/fail counts per evaluator

## Best Practices

### 1. Console + File Reporter

Use console for monitoring, file for archiving:

```yaml
reporters:
  - type: console    # Watch progress
  - type: html       # Save results
    output_path: ./report.html
```

### 2. Adjust Log Level

Control verbosity:

```yaml
agent:
  log_level: INFO    # Standard output
  # log_level: DEBUG # Verbose (shows all details)
  # log_level: WARNING # Quiet (only warnings/errors)

reporters:
  - type: console
```

### 3. Redirect Output

Capture console output to file:

```bash
# Save output to file
judge-llm run --config test.yaml > results.txt 2>&1

# Show on screen and save to file
judge-llm run --config test.yaml | tee results.txt
```

## Combining with Other Reporters

### Pattern 1: Dev Workflow

```yaml
reporters:
  - type: console              # Immediate feedback
  - type: html                 # Detailed analysis
    output_path: ./dev-report.html
```

### Pattern 2: CI Pipeline

```yaml
reporters:
  - type: console              # CI logs
  - type: json                 # Artifact storage
    output_path: ./results.json
```

### Pattern 3: Production Monitoring

```yaml
reporters:
  - type: console              # CloudWatch/logs
  - type: database             # Historical data
    db_path: ./prod-evals.db
```

## Troubleshooting

### Colors Not Showing

**Issue:** Output shows escape codes instead of colors

**Cause:** Terminal doesn't support ANSI colors

**Solutions:**
```bash
# Force color output
FORCE_COLOR=1 judge-llm run --config test.yaml

# Disable colors
NO_COLOR=1 judge-llm run --config test.yaml
```

### Output Cut Off

**Issue:** Long output truncated

**Cause:** Terminal buffer limit

**Solutions:**
- Increase terminal buffer size
- Redirect to file: `judge-llm run --config test.yaml > output.txt`
- Use HTML reporter for full details

### Unicode Errors

**Issue:** `UnicodeEncodeError` in console output

**Cause:** Terminal encoding doesn't support unicode

**Solutions:**
```bash
# Set UTF-8 encoding
export PYTHONIOENCODING=utf-8
judge-llm run --config test.yaml
```

## Related Documentation

- [Reporters Overview](./overview.md)
- [HTML Reporter](./html-reporter.md)
- [JSON Reporter](./json-reporter.md)
- [Database Reporter](./database-reporter.md)

## API Reference

For implementation details, see [ConsoleReporter API](../api-reference/reporters.md#consolereporter).
