---
sidebar_position: 4
---

# Cost Evaluator

Control evaluation budgets by setting maximum cost thresholds per test case.

## Overview

The **Cost Evaluator** ensures your evaluation costs stay within budget by:
- Tracking actual API costs per test case
- Comparing against configured maximums
- Failing tests that exceed cost limits
- Monitoring cost efficiency

**Key Features:**
- Per-test-case cost limits
- Automatic cost tracking from providers
- Currency support
- Cost ratio analysis
- Budget enforcement

## Configuration

### Basic Configuration

```yaml
evaluators:
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.10  # $0.10 per test case
```

### Full Configuration

```yaml
evaluators:
  - type: cost_evaluator
    enabled: true
    config:
      max_cost_per_case: 0.10   # Maximum cost in USD
      currency: USD             # Currency code
```

## Cost Tracking

### How Costs are Calculated

Providers automatically track costs:

1. **Token counting**: Count input/output tokens
2. **Pricing lookup**: Apply provider-specific rates
3. **Cost calculation**: tokens × rate
4. **Total aggregation**: Sum across all turns

**Example (Gemini):**
```
Input: 100 tokens × $0.00025/1K = $0.000025
Output: 50 tokens × $0.0005/1K = $0.000025
Total: $0.00005
```

### Provider Costs

| Provider | Input (per 1K tokens) | Output (per 1K tokens) |
|----------|----------------------|------------------------|
| **Gemini Flash** | $0.00025 | $0.0005 |
| **Gemini Pro** | $0.00125 | $0.005 |
| **Mock** | $0.00 | $0.00 |
| **Custom** | Varies | Varies |

## Setting Cost Limits

### By Test Complexity

```yaml
# Simple Q&A
max_cost_per_case: 0.001  # $0.001

# Multi-turn conversations
max_cost_per_case: 0.01   # $0.01

# Complex reasoning
max_cost_per_case: 0.10   # $0.10

# Large document processing
max_cost_per_case: 1.00   # $1.00
```

### By Budget

```yaml
# Total budget: $10 for 100 test cases
max_cost_per_case: 0.10  # $10 / 100 = $0.10 per case
```

## Usage Examples

### Example 1: Basic Cost Control

```yaml
# config.yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini
    agent_id: cost_aware_agent
    model: gemini-2.0-flash-exp

evaluators:
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.01

reporters:
  - type: console
```

Run evaluation:
```bash
judge-llm run --config config.yaml
```

### Example 2: Different Limits for Different Tests

```json
{
  "eval_id": "simple_qa_001",
  "conversation": [...],
  "evaluator_config": {
    "CostEvaluator": {
      "max_cost_per_case": 0.001  // Simple = cheap
    }
  }
},
{
  "eval_id": "complex_reasoning_001",
  "conversation": [...],
  "evaluator_config": {
    "CostEvaluator": {
      "max_cost_per_case": 0.10  // Complex = higher budget
    }
  }
}
```

### Example 3: Cost Comparison

Compare costs across providers:

```yaml
providers:
  - type: gemini
    agent_id: gemini_flash
    model: gemini-2.0-flash-exp
    
  - type: gemini
    agent_id: gemini_pro
    model: gemini-1.5-pro

evaluators:
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.05
  - type: response_evaluator

reporters:
  - type: html
    config:
      output_file: cost_comparison.html
```

View HTML report to compare costs.

### Example 4: Programmatic Cost Monitoring

```python
from judge_llm import evaluate

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{
        "type": "gemini",
        "agent_id": "test",
        "model": "gemini-2.0-flash-exp"
    }],
    evaluators=[{
        "type": "cost_evaluator",
        "config": {"max_cost_per_case": 0.01}
    }],
    reporters=[{"type": "console"}]
)

# Check total costs
print(f"Total cost: ${report.total_cost:.4f}")
print(f"Avg cost per case: ${report.total_cost / len(report.test_cases):.4f}")

# Find expensive test cases
for case in report.test_cases:
    if case.cost > 0.01:
        print(f"{case.eval_id}: ${case.cost:.4f} (over budget!)")
```

## Evaluation Result

The cost evaluator returns:

```python
{
    "evaluator_name": "CostEvaluator",
    "evaluator_type": "cost_evaluator",
    "passed": True,
    "score": 1.0,
    "threshold": 0.10,
    "success": True,
    "details": {
        "actual_cost": 0.000234,
        "max_cost": 0.10,
        "currency": "USD",
        "cost_ratio": 0.00234  # actual / max
    }
}
```

**Pass criteria:** `actual_cost ≤ max_cost_per_case`

### Failed Example

```python
{
    "passed": False,
    "score": 0.0,
    "details": {
        "actual_cost": 0.15,
        "max_cost": 0.10,
        "currency": "USD",
        "cost_ratio": 1.5  # 50% over budget
    }
}
```

## Cost Optimization Tips

### 1. Use Cheaper Models

```yaml
# Expensive
model: gemini-1.5-pro

# Cheaper (5x less)
model: gemini-2.0-flash-exp
```

### 2. Limit Response Length

```yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    max_tokens: 512  # Limit output tokens
```

### 3. Reduce Temperature

Lower temperature = more focused = fewer tokens:

```yaml
temperature: 0.3  # More focused, cheaper
```

### 4. Use Mock for Development

```yaml
# Development - Free
providers:
  - type: mock

# Production - Real costs
providers:
  - type: gemini
```

### 5. Batch Similar Tests

Group similar tests to benefit from caching (if provider supports it).

## Best Practices

### 1. Set Realistic Limits

Start generous, then tighten:

```yaml
# Week 1: Learn costs
max_cost_per_case: 1.00

# Week 2: Optimize based on data
max_cost_per_case: 0.10

# Week 3: Production limits
max_cost_per_case: 0.05
```

### 2. Monitor Trends

Track costs over time:
- Average cost per test case
- Total evaluation costs
- Cost by test case type
- Cost by provider

### 3. Use with Response Evaluator

Balance cost and quality:

```yaml
evaluators:
  - type: cost_evaluator
    config: {max_cost_per_case: 0.01}
  - type: response_evaluator
    config: {similarity_threshold: 0.8}
```

Find the sweet spot: good quality at reasonable cost.

### 4. Budget Alerts

Set up alerts for cost overruns:

```python
if report.total_cost > MONTHLY_BUDGET:
    send_alert(f"Budget exceeded: ${report.total_cost}")
```

## Troubleshooting

### All Tests Failing Cost Check

**Issue:** Every test exceeds cost limit

**Solutions:**

1. **Check limit is reasonable:**
   ```yaml
   max_cost_per_case: 0.000001  # Too low!
   max_cost_per_case: 0.01      # Better
   ```

2. **Use cheaper model:**
   ```yaml
   model: gemini-2.0-flash-exp  # Cheapest
   ```

3. **Reduce max_tokens:**
   ```yaml
   max_tokens: 512  # Limit response length
   ```

### Cost is Always $0.00

**Issue:** Provider not tracking costs

**Solutions:**

1. **Check provider type:**
   - Mock provider: Always $0 (expected)
   - Gemini provider: Should track costs

2. **Verify provider implementation:**
   Custom providers must calculate costs in `execute()`

### Unexpected High Costs

**Issue:** Costs higher than expected

**Causes:**
- Long conversations (many turns)
- Large input contexts
- High temperature (verbose responses)
- Wrong model selected

**Debug:**
```python
# Check token usage
for case in report.test_cases:
    print(f"{case.eval_id}:")
    print(f"  Tokens: {case.token_usage.total_tokens}")
    print(f"  Cost: ${case.cost:.4f}")
```

## Related Documentation

- [Evaluators Overview](./overview)
- [Response Evaluator](./response-evaluator)
- [Latency Evaluator](./latency-evaluator)
- [Gemini Provider Costs](../guides/configuration)

## API Reference

For implementation details, see the [CostEvaluator API Reference](../guides/python-api).
