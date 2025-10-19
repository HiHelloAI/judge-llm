---
sidebar_position: 4
---

# Comparing Models

Learn how to compare different LLM models side-by-side to find the best one for your use case.

## A/B Testing Models

Compare two models on the same test cases:

```yaml
# ab-test.yaml
dataset:
  loader: local_file
  paths:
    - ./tests.json

providers:
  - type: gemini
    agent_id: gemini_flash
    model: gemini-2.0-flash-exp
  
  - type: openai
    agent_id: gpt4
    model: gpt-4

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.05
  - type: latency_evaluator
    max_latency: 5.0

reporters:
  - type: console
  - type: html
    output_path: ./model-comparison.html
```

Run the comparison:
```bash
judge-llm run --config ab-test.yaml
```

## Understanding the Results

The HTML report shows:
- **Per-Model Success Rates**: Which model has higher accuracy
- **Cost Comparison**: Which model is more cost-effective
- **Latency Comparison**: Which model is faster
- **Test-by-Test Breakdown**: See where each model excels

### Example Output

```
Summary:
  
  gemini_flash:
    Total Tests: 10
    Passed: 9
    Failed: 1
    Success Rate: 90.0%
    Total Cost: $0.0087
    Avg Latency: 1.2s
  
  gpt4:
    Total Tests: 10
    Passed: 10
    Failed: 0
    Success Rate: 100.0%
    Total Cost: $0.0234
    Avg Latency: 2.1s
```

## Multi-Model Comparison

Compare 3+ models:

```yaml
providers:
  - type: gemini
    agent_id: gemini_flash
    model: gemini-2.0-flash-exp
  
  - type: gemini
    agent_id: gemini_pro
    model: gemini-pro
  
  - type: openai
    agent_id: gpt4
    model: gpt-4
  
  - type: anthropic
    agent_id: claude
    model: claude-3-5-sonnet-20241022
```

## Analyzing Results with Python

Use the Python API for deeper analysis:

```python
from judge_llm import evaluate
import pandas as pd

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[
        {"type": "gemini", "agent_id": "gemini"},
        {"type": "openai", "agent_id": "gpt4"},
        {"type": "anthropic", "agent_id": "claude"}
    ],
    evaluators=[{"type": "response_evaluator"}]
)

# Convert to DataFrame
data = []
for tc in report.test_cases:
    data.append({
        "test_id": tc.eval_id,
        "provider": tc.agent_id,
        "passed": tc.passed,
        "cost": tc.cost,
        "latency": tc.time_taken
    })

df = pd.DataFrame(data)

# Aggregate by provider
summary = df.groupby("provider").agg({
    "passed": ["count", "sum", "mean"],
    "cost": ["sum", "mean"],
    "latency": "mean"
}).round(4)

print("\nModel Comparison:")
print(summary)

# Find winner
best_accuracy = summary[("passed", "mean")].idxmax()
best_cost = summary[("cost", "sum")].idxmin()
best_speed = summary[("latency", "mean")].idxmin()

print(f"\nBest Accuracy: {best_accuracy}")
print(f"Best Cost: {best_cost}")
print(f"Best Speed: {best_speed}")
```

## Cost vs. Quality Tradeoff

Visualize cost vs. quality:

```python
import matplotlib.pyplot as plt

# Group by provider
providers = df.groupby("provider").agg({
    "passed": "mean",
    "cost": "sum"
})

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(providers["cost"], providers["passed"], s=100)

for provider in providers.index:
    plt.annotate(
        provider,
        (providers.loc[provider, "cost"], providers.loc[provider, "passed"]),
        xytext=(5, 5),
        textcoords="offset points"
    )

plt.xlabel("Total Cost ($)")
plt.ylabel("Success Rate")
plt.title("Model Comparison: Cost vs. Quality")
plt.grid(True, alpha=0.3)
plt.show()
```

## Testing Model Variants

Compare different configurations of the same model:

```yaml
providers:
  - type: gemini
    agent_id: gemini_temp_0
    model: gemini-2.0-flash-exp
    temperature: 0.0  # Deterministic
  
  - type: gemini
    agent_id: gemini_temp_0.7
    model: gemini-2.0-flash-exp
    temperature: 0.7  # Creative
  
  - type: gemini
    agent_id: gemini_temp_1.0
    model: gemini-2.0-flash-exp
    temperature: 1.0  # Very creative
```

## Winner Selection Strategy

### 1. Accuracy First

Choose the model with highest success rate:

```python
winner = df.groupby("provider")["passed"].mean().idxmax()
print(f"Most accurate model: {winner}")
```

### 2. Cost First

Choose the cheapest model that meets minimum quality:

```python
MIN_SUCCESS_RATE = 0.9

# Filter by minimum quality
qualified = df.groupby("provider").agg({
    "passed": "mean",
    "cost": "sum"
})
qualified = qualified[qualified["passed"] >= MIN_SUCCESS_RATE]

# Find cheapest among qualified
winner = qualified["cost"].idxmin()
print(f"Best value model: {winner}")
```

### 3. Speed First

Choose the fastest model:

```python
winner = df.groupby("provider")["latency"].mean().idxmin()
print(f"Fastest model: {winner}")
```

### 4. Balanced Scoring

Weight multiple factors:

```python
WEIGHTS = {
    "accuracy": 0.5,
    "cost": 0.3,
    "speed": 0.2
}

providers = df.groupby("provider").agg({
    "passed": "mean",
    "cost": "sum",
    "latency": "mean"
})

# Normalize (0-1 scale)
providers["accuracy_norm"] = providers["passed"]
providers["cost_norm"] = 1 - (providers["cost"] / providers["cost"].max())
providers["speed_norm"] = 1 - (providers["latency"] / providers["latency"].max())

# Calculate weighted score
providers["score"] = (
    providers["accuracy_norm"] * WEIGHTS["accuracy"] +
    providers["cost_norm"] * WEIGHTS["cost"] +
    providers["speed_norm"] * WEIGHTS["speed"]
)

winner = providers["score"].idxmax()
print(f"Best balanced model: {winner}")
print(f"Score: {providers.loc[winner, 'score']:.3f}")
```

## Storing Results for Tracking

Use database reporter to track comparisons over time:

```yaml
reporters:
  - type: console
  - type: database
    db_path: ./model_comparisons.db
```

Query historical data:

```sql
SELECT
    agent_id,
    AVG(passed) as avg_success_rate,
    AVG(cost) as avg_cost,
    AVG(time_taken) as avg_latency,
    COUNT(*) as total_tests
FROM test_cases
GROUP BY agent_id
ORDER BY avg_success_rate DESC;
```

## Best Practices

### 1. Use Same Test Set

Always compare models on identical test cases:

```yaml
dataset:
  loader: local_file
  paths:
    - ./tests.json  # Same for all models
```

### 2. Multiple Runs

Run each comparison multiple times for statistical significance:

```bash
for i in {1..5}; do
  judge-llm run --config ab-test.yaml --report database --db-path results.db
done
```

### 3. Diverse Test Cases

Include various scenarios:
- Simple factual questions
- Complex reasoning tasks
- Edge cases
- Multi-turn conversations

### 4. Control Variables

Keep other factors constant:
- Same temperature (unless testing temperature)
- Same system prompt
- Same evaluators
- Same test order

## Next Steps

- [Configuration Guide](../guides/configuration) - Advanced configuration options
- [Database Reporter](../reporters/database-reporter) - Track results over time
- [Cost Evaluator](../evaluators/cost-evaluator) - Budget control
- [Latency Evaluator](../evaluators/latency-evaluator) - Performance testing

## Related Documentation

- [Python API](../guides/python-api) - Programmatic analysis
- [HTML Reporter](../reporters/html-reporter) - Visual comparisons
- [Examples](../examples) - More comparison examples
