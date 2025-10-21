# Parallel Execution Guide

## Overview

Judge LLM supports parallel execution of test cases to speed up evaluation runs. When enabled, multiple test cases can be executed concurrently using a thread pool.

## Configuration

Enable parallel execution in your `config.yaml`:

```yaml
agent:
  name: my_agent
  num_runs: 1
  parallel_execution: true  # Enable parallel execution
  max_workers: 4            # Number of concurrent workers
```

### Parameters

- **`parallel_execution`** (boolean, default: `false`)
  - When `true`, executes test cases in parallel
  - When `false`, executes test cases sequentially

- **`max_workers`** (integer, default: `4`)
  - Maximum number of concurrent workers
  - Only used when `parallel_execution` is `true`
  - Recommended: Set to number of CPU cores or less

- **`num_runs`** (integer, default: `1`)
  - Number of times to run each test case
  - Each run is treated as a separate execution task
  - Total executions = `eval_cases × providers × num_runs`

## How It Works

### Sequential Execution

```
Task 1 ──> Task 2 ──> Task 3 ──> Task 4 ──> Task 5
  ↓         ↓         ↓         ↓         ↓
 0.2s      0.2s      0.2s      0.2s      0.2s
                Total: 1.0s
```

### Parallel Execution (4 workers)

```
Task 1 ──> (0.2s)
Task 2 ──> (0.2s)
Task 3 ──> (0.2s)     Total: ~0.3s (wall-clock)
Task 4 ──> (0.2s)
Task 5 ──> ──> (0.2s)
```

## Time Calculation

### Total Time

- **Sequential**: Sum of all individual execution times
- **Parallel**: Wall-clock time (actual elapsed time)

This means:
- Sequential: 5 tasks × 0.2s each = 1.0s total
- Parallel: All 5 tasks complete in ~0.3s (wall-clock)

### Individual Execution Times

Each execution still reports its own time:
- Provider execution time
- Evaluator execution time
- Total per-execution time

The framework tracks both:
- **Per-execution time**: Time for each individual task
- **Total time**: Wall-clock time for all executions

## Example

```yaml
# config.yaml
agent:
  name: my_agent
  num_runs: 2              # Run each test twice
  parallel_execution: true # Run in parallel
  max_workers: 4           # Use 4 workers

dataset:
  loader: local_file
  paths:
    - ./tests.yaml  # Contains 5 test cases

providers:
  - type: gemini
    agent_id: test_agent
```

**Total Executions**: 5 cases × 1 provider × 2 runs = **10 executions**

With parallel execution (4 workers):
- Worker 1: Executes 3 tasks
- Worker 2: Executes 3 tasks
- Worker 3: Executes 2 tasks
- Worker 4: Executes 2 tasks

If each task takes ~0.5s:
- **Sequential**: 10 × 0.5s = 5.0s
- **Parallel (4 workers)**: ~1.5s (wall-clock)
- **Speedup**: ~3.3x

## Best Practices

### When to Use Parallel Execution

✅ **Good for:**
- Large number of test cases (>10)
- Independent test cases
- API-based providers (I/O bound)
- Long-running evaluations

❌ **Avoid for:**
- Small number of test cases (<5)
- Tests with shared state
- CPU-intensive local models
- Memory-constrained environments

### Choosing max_workers

- **I/O-bound tasks** (API calls): Can use more workers (8-16)
- **CPU-bound tasks** (local models): Use CPU cores or less (4-8)
- **Memory-constrained**: Reduce workers to avoid OOM

```yaml
# For API-based agents
max_workers: 16

# For local models
max_workers: 4

# For memory-constrained
max_workers: 2
```

### Provider Compatibility

All providers support parallel execution:
- ✅ **Gemini Provider**: Thread-safe, works well in parallel
- ✅ **ADK Provider**: Thread-safe with `asyncio.run()` per execution
- ✅ **Mock Provider**: Thread-safe
- ✅ **Custom Providers**: Ensure thread-safety

## Thread Safety

When implementing custom providers, ensure:

1. **No shared mutable state** between executions
2. **Thread-safe API clients** or create new clients per execution
3. **Proper resource cleanup** in finally blocks or context managers

Example thread-safe provider:

```python
class MyProvider(BaseProvider):
    def execute(self, eval_case: EvalCase) -> ProviderResult:
        # Create new client per execution (thread-safe)
        client = create_api_client()

        try:
            result = client.execute(eval_case)
            return result
        finally:
            client.close()  # Clean up
```

## Troubleshooting

### Parallel execution slower than sequential

**Possible causes:**
- Too many workers (context switching overhead)
- Provider not thread-safe (serializing access)
- Small/fast test cases (overhead > benefit)

**Solutions:**
- Reduce `max_workers`
- Check provider thread-safety
- Use sequential for small test sets

### Resource exhaustion

**Symptoms:**
- Out of memory errors
- Connection pool exhausted
- Rate limiting errors

**Solutions:**
- Reduce `max_workers`
- Add delays between executions
- Implement connection pooling
- Add rate limiting to provider

### Inconsistent results

**Possible causes:**
- Shared state between executions
- Race conditions in provider
- Non-deterministic agent behavior

**Solutions:**
- Ensure test case independence
- Review provider for shared state
- Add synchronization if needed

## Performance Metrics

Reports show:
- **Total Executions**: Number of tasks executed
- **Total Time**: Wall-clock time (parallel) or sum (sequential)
- **Avg Time/Execution**: Average time per task
- **Success Rate**: Percentage of successful executions

Example output:

```
Summary
┌─────────────────────┬──────────┐
│ Metric              │ Value    │
├─────────────────────┼──────────┤
│ Total Executions    │ 10       │
│ Success Rate        │ 100.0%   │
│ Total Cost          │ $0.0050  │
│ Total Time          │ 1.5s     │  ← Wall-clock (parallel)
│ Avg Time/Execution  │ 0.5s     │  ← Per-execution avg
└─────────────────────┴──────────┘
```

## See Also

- [Configuration Guide](configuration.md)
- [Provider Development](providers.md)
- [Performance Optimization](performance.md)
