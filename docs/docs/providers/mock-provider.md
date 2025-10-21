---
sidebar_position: 3
---

# Mock Provider

The Mock Provider is a built-in test provider that returns expected responses without making any API calls. Perfect for testing, development, and CI/CD environments where you want fast feedback without API costs.

## Overview

**Type:** `mock`

**Purpose:** Test evaluation logic and framework functionality without external API dependencies.

**Key Features:**
- ✅ Zero API calls - instant execution
- ✅ No authentication required
- ✅ Mock cost and token tracking
- ✅ Supports all evaluation types
- ✅ Perfect for development and testing
- ✅ No rate limits
- ✅ Deterministic results

## Quick Start

### Basic Configuration

```yaml
providers:
  - type: mock
    agent_id: test_agent
```

That's it! No API keys or additional configuration needed.

### Run Evaluation

```bash
judge-llm run --config config.yaml
# Completes instantly with no API costs
```

## How It Works

The Mock Provider:

1. **Reads expected responses** from your test cases
2. **Returns them as-is** (no LLM call)
3. **Calculates mock costs** based on text length
4. **Tracks execution time** (near-zero)

### Example Flow

**Input (evalset.yaml):**
```yaml
eval_cases:
  - eval_id: test_1
    conversation:
      - invocation_id: turn_1
        user_content:
          parts:
            - text: "What is 2+2?"
        final_response:
          parts:
            - text: "The answer is 4"  # Expected response
```

**Output:**
```
✓ test_1: Response matches expected
Cost: $0.0001 (mocked)
Time: 0.001s
```

The Mock Provider returns "The answer is 4" exactly as specified in the test case.

## Configuration Options

### Minimal Configuration

```yaml
providers:
  - type: mock
    agent_id: baseline
```

### With Metadata (Optional)

```yaml
providers:
  - type: mock
    agent_id: test_baseline
    metadata:
      description: "Test baseline for development"
      version: "1.0"
```

### Configuration Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | string | - | Must be `mock` |
| `agent_id` | string | - | Unique identifier |
| `metadata` | object | `{}` | Optional metadata |

## Use Cases

### 1. Development & Testing

Test your evaluation logic before using real LLMs:

```yaml
# Start with mock provider
providers:
  - type: mock
    agent_id: dev_baseline

# Later switch to real provider
# providers:
#   - type: gemini
#     agent_id: production
```

### 2. CI/CD Pipelines

Run tests in CI without API costs:

```yaml
# .github/workflows/test.yml
agent:
  fail_on_threshold_violation: true  # Fail CI on quality issues

providers:
  - type: mock
    agent_id: ci_baseline

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 1.0  # Exact match required
```

### 3. Framework Development

Test Judge LLM features:

```yaml
providers:
  - type: mock
    agent_id: feature_test

# Test parallel execution
agent:
  parallel_execution: true
  max_workers: 8
```

### 4. Evaluator Development

Test custom evaluators without API calls:

```yaml
providers:
  - type: mock
    agent_id: evaluator_test

evaluators:
  - type: custom
    module_path: ./my_evaluators/new_evaluator.py
    class_name: NewEvaluator
```

### 5. Baseline Comparison

Compare real LLM against expected responses:

```yaml
providers:
  # Mock provider as baseline (expected responses)
  - type: mock
    agent_id: expected_baseline

  # Real LLM for comparison
  - type: gemini
    agent_id: actual_model
```

## Mock Cost Calculation

The Mock Provider simulates costs for testing:

```python
# Mock cost formula
total_tokens = len(prompt_text) + len(response_text)
mock_cost = total_tokens * 0.00001  # $0.00001 per token
```

### Viewing Mock Costs

```python
from judge_llm import evaluate

report = evaluate(config="config.yaml")

# Total mock cost
print(f"Mock cost: ${report.total_cost:.6f}")

# Per-case costs
for run in report.execution_runs:
    if run.provider_type == "mock":
        print(f"{run.eval_case_id}: ${run.provider_result.cost:.6f}")
```

## Mock Token Usage

Token counts are simulated based on text length:

```python
for run in report.execution_runs:
    tokens = run.provider_result.token_usage
    print(f"Prompt: {tokens['prompt_tokens']}")
    print(f"Completion: {tokens['completion_tokens']}")
    print(f"Total: {tokens['total_tokens']}")
```

## Multi-turn Conversations

Mock Provider supports multi-turn conversations:

```yaml
eval_cases:
  - eval_id: multi_turn
    conversation:
      # Turn 1
      - invocation_id: turn_1
        user_content:
          parts:
            - text: "Hi"
        final_response:
          parts:
            - text: "Hello!"

      # Turn 2
      - invocation_id: turn_2
        user_content:
          parts:
            - text: "How are you?"
        final_response:
          parts:
            - text: "I'm doing well, thanks!"
```

Each turn is returned exactly as specified.

## Performance

### Execution Speed

```bash
# Mock Provider: ~0.001s per test case
# Gemini Provider: ~1-3s per test case

# 100 test cases:
# Mock: ~0.1s total
# Gemini: ~100-300s total
```

### Parallel Execution

Mock Provider works great with parallel execution:

```yaml
agent:
  parallel_execution: true
  max_workers: 16  # High parallelism possible (no rate limits)

providers:
  - type: mock
    agent_id: parallel_test
```

## Examples

### Example 1: Quick Test

```yaml
# config.yaml
dataset:
  loader: local_file
  paths: [./tests.yaml]

providers:
  - type: mock
    agent_id: quick_test

evaluators:
  - type: response_evaluator
```

```bash
# Runs instantly
judge-llm run --config config.yaml
```

### Example 2: CI/CD Integration

```yaml
# ci-config.yaml
agent:
  fail_on_threshold_violation: true  # Fail build on errors
  parallel_execution: true
  max_workers: 8

dataset:
  loader: local_file
  paths: [./tests/*.yaml]

providers:
  - type: mock
    agent_id: ci_test

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 1.0  # Require exact match

  - type: trajectory_evaluator
    config:
      sequence_match_type: exact

reporters:
  - type: json
    output_path: ./test-results.json
```

### Example 3: Baseline vs Real LLM

```yaml
providers:
  # Expected responses (baseline)
  - type: mock
    agent_id: expected

  # Actual LLM output
  - type: gemini
    agent_id: gemini_flash
    model: gemini-2.0-flash-exp

# Compare both against expected responses
evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.85
```

## Limitations

### What Mock Provider Doesn't Do

❌ **No Real LLM Calls**
- Returns expected responses only
- No actual model inference

❌ **No Tool Calling**
- Doesn't simulate function calls
- Returns static responses

❌ **No Variability**
- Always returns the same response
- No temperature/randomness

❌ **No Context Building**
- Doesn't maintain conversation state
- Each turn is independent

### When NOT to Use Mock Provider

Don't use Mock Provider for:
- **Production Testing** - Use real LLM providers
- **Response Quality** - Can't test actual LLM behavior
- **Prompt Engineering** - No real model to test prompts
- **Tool/Function Testing** - Use Google ADK or real providers

## Testing Strategy

### Recommended Workflow

1. **Start with Mock** - Validate test cases and evaluation logic
2. **Switch to Real** - Test actual LLM behavior
3. **Use Both** - Compare expected vs actual

```yaml
# Phase 1: Validate tests with mock
providers:
  - type: mock
    agent_id: validation

# Phase 2: Test real LLM
# providers:
#   - type: gemini
#     agent_id: real_test

# Phase 3: Compare both
# providers:
#   - type: mock
#     agent_id: expected
#   - type: gemini
#     agent_id: actual
```

## Advantages

### ✅ Speed
- Instant execution (no API latency)
- High parallelism (no rate limits)
- Fast iteration cycles

### ✅ Cost
- Zero API costs
- Unlimited test runs
- Perfect for CI/CD

### ✅ Reliability
- Deterministic results
- No network issues
- No service outages

### ✅ Development
- Test framework features
- Validate test cases
- Debug evaluation logic

## Related Documentation

- [Providers Overview](./overview) - All provider types
- [Gemini Provider](./gemini-provider) - Real LLM testing
- [Google ADK Provider](./google-adk-provider) - Agent testing
- [Custom Providers](./custom-providers) - Implement your own

## Next Steps

- Use Mock Provider to validate your test cases
- Switch to [Gemini Provider](./gemini-provider) for real testing
- Combine both for baseline comparisons
- Implement [Custom Providers](./custom-providers) for other LLMs
