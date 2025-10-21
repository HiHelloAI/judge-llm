---
sidebar_position: 1
---

# Evaluators Overview

Evaluators judge the quality of LLM responses by analyzing provider outputs against expected criteria. They are the core assessment engine of Judge LLM.

## What are Evaluators?

An **Evaluator** is a component that:
- Analyzes LLM responses from providers
- Compares actual outputs against expected results
- Checks performance metrics (cost, latency, tokens)
- Returns pass/fail verdicts with detailed feedback
- Supports custom evaluation logic

## Available Evaluators

### Built-in Evaluators

| Evaluator | Purpose | Key Metrics | Best For |
|-----------|---------|-------------|----------|
| **[Response](./response-evaluator)** | Response quality | Similarity, exact match | Answer correctness |
| **[Trajectory](./trajectory-evaluator)** | Conversation flow | Turn count, structure | Multi-turn dialogues |
| **[Cost](./cost-evaluator)** | Budget control | Total cost, per-case cost | Cost optimization |
| **[Latency](./latency-evaluator)** | Performance | Response time, timeouts | Speed requirements |

### Custom Evaluators

Create [custom evaluators](./custom-evaluators) for:
- Domain-specific validation
- Safety and compliance checks
- Business rule enforcement
- Advanced quality metrics

## How Evaluators Work

### 1. Evaluation Flow

```
Provider Result → Evaluator(s) → Pass/Fail + Feedback → Report
```

1. **Provider executes** test case, returns responses + metadata
2. **Evaluator receives** provider result and expected outputs
3. **Evaluator analyzes** responses using configured criteria
4. **Evaluator returns** evaluation result with score and feedback
5. **Reporter generates** summary of all evaluations

### 2. Evaluation Result

Each evaluator returns an `EvaluatorResult`:

```python
{
    "evaluator_name": "ResponseEvaluator",
    "evaluator_type": "response_evaluator",
    "passed": True,
    "score": 0.95,
    "threshold": 0.8,
    "success": True,
    "details": {
        "match_type": "rouge",
        "average_score": 0.95,
        "num_invocations": 3
    }
}
```

### 3. Multiple Evaluators

Run multiple evaluators in parallel:

```yaml
evaluators:
  - type: response_evaluator
    config: {similarity_threshold: 0.8}

  - type: cost_evaluator
    config: {max_cost_per_case: 0.10}

  - type: latency_evaluator
    config: {max_latency_seconds: 5.0}
```

All evaluators must pass for the test case to succeed.

## Configuration

### Basic Configuration

```yaml
evaluators:
  - type: response_evaluator
    enabled: true
```

### Full Configuration

```yaml
evaluators:
  - type: response_evaluator
    enabled: true
    config:
      similarity_threshold: 0.8
      match_type: semantic
      case_sensitive: false

  - type: custom
    module_path: ./my_evaluators/safety.py
    class_name: SafetyEvaluator
    enabled: true
    config:
      check_toxicity: true
      severity_threshold: "medium"
```

### Per-Test-Case Override

Override evaluator settings for specific test cases:

```json
{
  "eval_id": "test_001",
  "conversation": [...],
  "evaluator_config": {
    "ResponseEvaluator": {
      "similarity_threshold": 0.9,
      "match_type": "exact"
    },
    "CostEvaluator": {
      "max_cost_per_case": 0.05
    }
  }
}
```

## Evaluator Selection Guide

### Response Evaluator

**Use when:**
- Checking answer correctness
- Validating response content
- Comparing against expected outputs
- Testing factual accuracy

**Example:** Math problems, factual Q&A, translation tasks

### Trajectory Evaluator

**Use when:**
- Validating conversation structure
- Checking multi-turn dialogues
- Ensuring proper turn-taking
- Verifying conversation depth

**Example:** Customer support flows, dialogue systems

### Cost Evaluator

**Use when:**
- Controlling API spending
- Budgeting evaluations
- Comparing provider costs
- Optimizing token usage

**Example:** Production budgets, cost comparison studies

### Latency Evaluator

**Use when:**
- Meeting performance SLAs
- Testing response speed
- Comparing provider latency
- Detecting timeouts

**Example:** Real-time applications, performance testing

## Evaluation Strategies

### Strategy 1: Quality-First

Focus on response accuracy:

```yaml
evaluators:
  - type: response_evaluator
    config: {similarity_threshold: 0.9}  # High bar
  - type: trajectory_evaluator
    config: {sequence_match_type: exact}
```

### Strategy 2: Cost-Optimized

Balance quality and cost:

```yaml
evaluators:
  - type: response_evaluator
    config: {similarity_threshold: 0.7}  # Lower threshold
  - type: cost_evaluator
    config: {max_cost_per_case: 0.01}  # Strict budget
```

### Strategy 3: Performance-Critical

Prioritize speed:

```yaml
evaluators:
  - type: latency_evaluator
    config: {max_latency_seconds: 2.0}  # Fast responses
  - type: response_evaluator
    config: {similarity_threshold: 0.75}  # Moderate quality
```

## Best Practices

### 1. Start Simple

Begin with basic evaluators:

```yaml
evaluators:
  - type: response_evaluator
```

Add more as needed.

### 2. Set Appropriate Thresholds

Don't over-optimize:

```yaml
# Too strict - may fail unnecessarily
similarity_threshold: 0.99

# Better - allows reasonable variation
similarity_threshold: 0.8
```

### 3. Use Multiple Evaluators

Combine different perspectives:

```yaml
evaluators:
  - type: response_evaluator  # Quality
  - type: cost_evaluator      # Budget
  - type: latency_evaluator   # Speed
```

### 4. Monitor Evaluation Metrics

Track evaluator performance:
- Pass rates per evaluator
- Score distributions
- Common failure patterns
- Threshold effectiveness

### 5. Leverage Per-Case Config

Override for edge cases:

```json
{
  "eval_id": "complex_reasoning_001",
  "evaluator_config": {
    "ResponseEvaluator": {
      "similarity_threshold": 0.7  // Lower for harder tasks
    }
  }
}
```

## Common Patterns

### Pattern 1: Baseline Testing

Compare against baseline provider:

```yaml
providers:
  - type: mock
    agent_id: baseline
  - type: gemini
    agent_id: test

evaluators:
  - type: response_evaluator
    config: {similarity_threshold: 0.8}
```

### Pattern 2: Progressive Evaluation

Run quick evaluators first:

```yaml
evaluators:
  - type: latency_evaluator  # Fast check
  - type: cost_evaluator     # Fast check
  - type: response_evaluator # Detailed analysis
```

### Pattern 3: Safety Gates

Use custom evaluators as gates:

```yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
  - type: response_evaluator  # Only if safe
```

## Troubleshooting

### All Tests Failing

**Issue:** Every test case fails evaluation

**Solutions:**
- Check similarity thresholds (may be too strict)
- Verify expected responses in evalset
- Review provider outputs in reports
- Lower thresholds temporarily to debug

### Inconsistent Results

**Issue:** Same test case passes/fails randomly

**Causes:**
- Provider non-determinism (high temperature)
- Fuzzy similarity matching
- Floating-point precision

**Solutions:**
- Use lower temperature for deterministic outputs
- Use exact match for consistent tests
- Set appropriate tolerances

### Evaluator Not Running

**Issue:** Evaluator not appearing in reports

**Solutions:**
- Check `enabled: true` in config
- Verify evaluator type is correct
- Check for errors in logs
- Ensure evaluator is properly imported

## Next Steps

- [Response Evaluator](./response-evaluator) - Validate response quality
- [Trajectory Evaluator](./trajectory-evaluator) - Check conversation structure
- [Cost Evaluator](./cost-evaluator) - Control spending
- [Latency Evaluator](./latency-evaluator) - Measure performance
- [Custom Evaluators](./custom-evaluators) - Build your own

## API Reference

For implementation details, see the [BaseEvaluator API Reference](../guides/python-api).
