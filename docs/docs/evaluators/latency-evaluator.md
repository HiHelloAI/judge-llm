---
sidebar_position: 5
---

# Latency Evaluator

Ensure agent performance meets speed requirements by measuring response times.

## Overview

The **Latency Evaluator** monitors agent response times and fails tests that exceed latency thresholds. Essential for:
- Performance SLAs
- Real-time applications
- User experience requirements
- Timeout detection

**Key Features:**
- Per-test-case latency limits
- Automatic timing from providers
- Percentile-based thresholds
- Performance ratio analysis

## Configuration

### Basic Configuration

```yaml
evaluators:
  - type: latency_evaluator
    config:
      max_latency_seconds: 5.0  # 5 second limit
```

### Full Configuration

```yaml
evaluators:
  - type: latency_evaluator
    enabled: true
    config:
      max_latency_seconds: 5.0  # Maximum allowed latency
      percentile: 100           # Percentile to evaluate (100 = max)
```

## Latency Measurement

### How Latency is Tracked

Providers measure end-to-end execution time:

```python
start_time = time.time()
# Execute all conversation turns
# Call LLM API
# Process responses
end_time = time.time()

latency = end_time - start_time  # Total seconds
```

**Includes:**
- API call time
- Network round trips
- Response processing
- All conversation turns

### Typical Latencies

| Provider | Model | Typical Range | Notes |
|----------|-------|---------------|-------|
| **Mock** | mock-model | 1-10ms | Instant (no API) |
| **Gemini** | flash-exp | 500-2000ms | Fast, varies by load |
| **Gemini** | 1.5-pro | 1000-3000ms | Slower, better quality |

## Setting Latency Limits

### By Application Type

```yaml
# Real-time chat - Very strict
max_latency_seconds: 1.0

# Interactive Q&A - Moderate
max_latency_seconds: 3.0

# Background processing - Lenient
max_latency_seconds: 10.0

# Batch evaluation - Very lenient
max_latency_seconds: 30.0
```

### By SLA Requirements

```yaml
# 99th percentile must be < 2s
max_latency_seconds: 2.0
percentile: 99

# Max latency must be < 5s
max_latency_seconds: 5.0
percentile: 100
```

## Usage Examples

### Example 1: Basic Performance Check

```yaml
# config.yaml
dataset:
  loader: local_file
  paths: [./perf_tests.json]

providers:
  - type: gemini
    agent_id: fast_agent
    model: gemini-2.0-flash-exp

evaluators:
  - type: latency_evaluator
    config:
      max_latency_seconds: 3.0

reporters:
  - type: console
```

### Example 2: Real-Time Requirements

```yaml
evaluators:
  - type: latency_evaluator
    config:
      max_latency_seconds: 1.0  # Strict 1s limit

  - type: response_evaluator
    config:
      similarity_threshold: 0.75  # Lower quality bar for speed
```

### Example 3: Per-Test-Case Limits

```json
{
  "eval_id": "simple_qa_001",
  "conversation": [...],
  "evaluator_config": {
    "LatencyEvaluator": {
      "max_latency_seconds": 1.0  // Quick questions = fast
    }
  }
},
{
  "eval_id": "complex_analysis_001",
  "conversation": [...],
  "evaluator_config": {
    "LatencyEvaluator": {
      "max_latency_seconds": 10.0  // Complex = slower OK
    }
  }
}
```

### Example 4: Provider Comparison

Compare latency across providers:

```yaml
providers:
  - type: gemini
    agent_id: flash
    model: gemini-2.0-flash-exp
    
  - type: gemini
    agent_id: pro
    model: gemini-1.5-pro

evaluators:
  - type: latency_evaluator
    config:
      max_latency_seconds: 5.0

reporters:
  - type: html
    config:
      output_file: latency_comparison.html
```

### Example 5: Programmatic Monitoring

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
        "type": "latency_evaluator",
        "config": {"max_latency_seconds": 3.0}
    }],
    reporters=[{"type": "console"}]
)

# Calculate percentiles
latencies = [case.time_taken for case in report.test_cases]
latencies.sort()

p50 = latencies[len(latencies) // 2]
p95 = latencies[int(len(latencies) * 0.95)]
p99 = latencies[int(len(latencies) * 0.99)]

print(f"P50: {p50:.2f}s")
print(f"P95: {p95:.2f}s")
print(f"P99: {p99:.2f}s")

# Find slow test cases
for case in report.test_cases:
    if case.time_taken > 5.0:
        print(f"Slow: {case.eval_id} ({case.time_taken:.2f}s)")
```

## Evaluation Result

The latency evaluator returns:

```python
{
    "evaluator_name": "LatencyEvaluator",
    "evaluator_type": "latency_evaluator",
    "passed": True,
    "score": 1.0,
    "threshold": 5.0,
    "success": True,
    "details": {
        "actual_latency_seconds": 1.234,
        "max_latency_seconds": 5.0,
        "latency_ratio": 0.247,  # 24.7% of max
        "percentile": 100
    }
}
```

**Pass criteria:** `actual_latency ≤ max_latency_seconds`

### Failed Example

```python
{
    "passed": False,
    "score": 0.0,
    "details": {
        "actual_latency_seconds": 6.5,
        "max_latency_seconds": 5.0,
        "latency_ratio": 1.3  # 30% over limit
    }
}
```

## Performance Optimization

### 1. Use Faster Models

```yaml
# Slower
model: gemini-1.5-pro

# Faster (2-3x)
model: gemini-2.0-flash-exp
```

### 2. Reduce Response Length

```yaml
providers:
  - type: gemini
    max_tokens: 256  # Shorter = faster
```

### 3. Use Lower Temperature

```yaml
temperature: 0.3  # More focused = faster
```

### 4. Optimize Prompts

- Shorter prompts = faster
- Clear instructions = fewer tokens
- Avoid unnecessary context

### 5. Parallel Execution

```yaml
agent:
  parallel_execution: true
  max_workers: 4  # Run 4 tests concurrently
```

Note: Doesn't improve individual test latency, but speeds up total evaluation.

## Best Practices

### 1. Set Realistic Limits

Account for network variability:

```yaml
# Too strict (may fail due to network)
max_latency_seconds: 0.5

# Better (accounts for variance)
max_latency_seconds: 3.0
```

### 2. Test Under Load

Run performance tests with concurrent requests to simulate real load.

### 3. Monitor Trends

Track latency over time:
- Detect performance regressions
- Identify slow test cases
- Optimize based on data

### 4. Balance Speed and Quality

```yaml
evaluators:
  # Speed matters
  - type: latency_evaluator
    config: {max_latency_seconds: 2.0}
  
  # But quality too
  - type: response_evaluator
    config: {similarity_threshold: 0.75}
```

### 5. Use Appropriate Percentiles

```yaml
# Average case
percentile: 50

# Most cases
percentile: 95

# Worst case (default)
percentile: 100
```

## Troubleshooting

### All Tests Failing Latency

**Issue:** Every test exceeds latency limit

**Solutions:**

1. **Check limit is realistic:**
   ```yaml
   max_latency_seconds: 0.1  # Too strict!
   max_latency_seconds: 3.0  # Better
   ```

2. **Use faster model:**
   ```yaml
   model: gemini-2.0-flash-exp
   ```

3. **Reduce response length:**
   ```yaml
   max_tokens: 256
   ```

4. **Check network:**
   - Slow connection?
   - High latency to API?
   - Try from different network

### Inconsistent Latency

**Issue:** Same test varies widely in latency

**Causes:**
- Network variability
- API server load
- Time of day effects

**Solutions:**
- Run multiple times and average
- Use percentile thresholds (p95, p99)
- Test at different times

### Mock Provider Too Fast

**Issue:** Mock provider passes all latency tests

**Expected:** Mock is instant (~1ms), this is normal

**Solution:** Only use latency evaluator with real providers

## Related Documentation

- [Evaluators Overview](./overview.md)
- [Cost Evaluator](./cost-evaluator.md)
- [Response Evaluator](./response-evaluator.md)
- [Performance Optimization](../guides/optimization.md)

## API Reference

For implementation details, see the [LatencyEvaluator API Reference](../api-reference/base-classes.md#latencyevaluator).
