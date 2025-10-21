---
sidebar_position: 2
---

# Your First Evaluation

Run your first LLM evaluation in 5 minutes and understand the results.

## Step 1: Create Test Cases

Create a file called `my-tests.json` with some simple test cases:

```json
[
  {
    "eval_id": "math_simple",
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
  },
  {
    "eval_id": "capital_france",
    "turns": [
      {
        "role": "user",
        "content": "What is the capital of France?"
      },
      {
        "role": "assistant",
        "content": "Paris",
        "expected": true
      }
    ]
  },
  {
    "eval_id": "greeting",
    "turns": [
      {
        "role": "user",
        "content": "Hello!"
      },
      {
        "role": "assistant",
        "content": "Hello! How can I help you today?",
        "expected": true
      }
    ]
  }
]
```

## Step 2: Create Configuration

Create a file called `my-config.yaml`:

```yaml
dataset:
  loader: local_file
  paths:
    - ./my-tests.json

providers:
  - type: gemini
    agent_id: my_first_agent
    model: gemini-2.0-flash-exp
    temperature: 0.0

evaluators:
  - type: response_evaluator
    llm_provider: gemini

reporters:
  - type: console
```

## Step 3: Run Evaluation

```bash
judge-llm run --config my-config.yaml
```

## Understanding the Output

You'll see output like this:

```
Starting evaluation...

Evaluation Progress:
  math_simple: ✓ PASSED (cost: $0.0012, time: 1.2s)
  capital_france: ✓ PASSED (cost: $0.0015, time: 1.5s)
  greeting: ✓ PASSED (cost: $0.0010, time: 1.0s)

Summary:
  Total Tests: 3
  Passed: 3
  Failed: 0
  Success Rate: 100.0%
  Total Cost: $0.0037
  Total Time: 3.7s
```

### What Each Part Means

**Evaluation Progress:**
- `math_simple: ✓ PASSED` - Test ID and pass/fail status
- `cost: $0.0012` - API cost for this test
- `time: 1.2s` - Execution time

**Summary:**
- `Total Tests: 3` - Number of test cases run
- `Passed: 3` - Number of tests that passed
- `Success Rate: 100.0%` - Percentage of tests passed
- `Total Cost: $0.0037` - Combined API cost
- `Total Time: 3.7s` - Total execution time

## Step 4: Try Different Outputs

### Save to JSON

```yaml
reporters:
  - type: console
  - type: json
    output_path: ./results.json
```

Run again:
```bash
judge-llm run --config my-config.yaml
```

Check the JSON output:
```bash
cat results.json | python -m json.tool
```

### Generate HTML Report

```yaml
reporters:
  - type: console
  - type: html
    output_path: ./report.html
```

Run and open the report:
```bash
judge-llm run --config my-config.yaml
open report.html  # On Mac
# Or: xdg-open report.html  # On Linux
# Or: start report.html  # On Windows
```

## Step 5: Add More Evaluators

Let's add cost and latency checks:

```yaml
dataset:
  loader: local_file
  paths:
    - ./my-tests.json

providers:
  - type: gemini
    agent_id: my_first_agent

evaluators:
  - type: response_evaluator
    llm_provider: gemini
  - type: cost_evaluator
    max_cost: 0.01  # Fail if cost > $0.01
  - type: latency_evaluator
    max_latency: 5.0  # Fail if latency > 5 seconds

reporters:
  - type: console
```

Run again:
```bash
judge-llm run --config my-config.yaml
```

Now you'll see multiple evaluator results per test:

```
Evaluation Progress:
  math_simple: ✓ PASSED (cost: $0.0012, time: 1.2s)
    ✓ response_evaluator: Response is correct
    ✓ cost_evaluator: Cost within limit ($0.0012 < $0.01)
    ✓ latency_evaluator: Latency within limit (1.2s < 5.0s)
```

## Common Patterns

### Test Multiple Models

Compare different models:

```yaml
providers:
  - type: gemini
    agent_id: gemini_flash
    model: gemini-2.0-flash-exp
  
  - type: openai
    agent_id: gpt4
    model: gpt-4

evaluators:
  - type: response_evaluator

reporters:
  - type: html
    output_path: ./comparison.html
```

### Multi-Turn Conversations

Test conversations with multiple exchanges:

```json
{
  "eval_id": "conversation_test",
  "turns": [
    {
      "role": "user",
      "content": "My name is Alice."
    },
    {
      "role": "assistant",
      "content": "Nice to meet you, Alice!",
      "expected": true
    },
    {
      "role": "user",
      "content": "What's my name?"
    },
    {
      "role": "assistant",
      "content": "Your name is Alice.",
      "expected": true
    }
  ]
}
```

### System Prompts

Include system instructions:

```json
{
  "eval_id": "with_system_prompt",
  "turns": [
    {
      "role": "system",
      "content": "You are a helpful math tutor. Always show your work."
    },
    {
      "role": "user",
      "content": "What is 15 * 3?"
    },
    {
      "role": "assistant",
      "content": "15 * 3 = 45\nBreaking it down: 15 + 15 + 15 = 45",
      "expected": true
    }
  ]
}
```

## What You've Learned

✅ Created test cases in JSON format  
✅ Configured providers and evaluators  
✅ Ran your first evaluation  
✅ Understood the output  
✅ Generated different report formats  
✅ Added multiple evaluators  

## Next Steps

Now you're ready to:

- [Explore Examples](../examples) - See more advanced examples
- [Learn Configuration](../guides/configuration) - Master all config options
- [Create Custom Evaluators](../evaluators/custom-evaluators) - Build domain-specific evaluators
- [Use Python API](../guides/python-api) - Run evaluations programmatically

## Troubleshooting

### Tests Not Passing

If your tests are failing, check:

1. **Is the expected response correct?**
   ```json
   {
     "role": "assistant",
     "content": "4",  // Make sure this is what you expect
     "expected": true
   }
   ```

2. **Are you using the right evaluator?**
   - Response evaluator checks correctness
   - Cost evaluator checks budget
   - Latency evaluator checks speed

3. **Check the reason in output:**
   ```
   test_001: ✗ FAILED
     ✗ response_evaluator: Response is incorrect
   ```

### High Costs

If costs are too high:

1. **Add cost evaluator:**
   ```yaml
   evaluators:
     - type: cost_evaluator
       max_cost: 0.01
   ```

2. **Use cheaper models:**
   ```yaml
   providers:
     - type: gemini
       model: gemini-2.0-flash-exp  # Cheaper than gemini-pro
   ```

### Slow Execution

If evaluations are slow:

1. **Add latency evaluator to find slow tests:**
   ```yaml
   evaluators:
     - type: latency_evaluator
       max_latency: 3.0
   ```

2. **Use faster models**
3. **Reduce test complexity**

## Quick Reference

### File Structure
```
project/
├── my-tests.json      # Test cases
├── my-config.yaml     # Configuration
├── .env               # API keys
└── results/           # Output reports
```

### Basic Commands
```bash
# Run evaluation
judge-llm run --config my-config.yaml

# Validate config
judge-llm validate --config my-config.yaml

# List available components
judge-llm list providers
judge-llm list evaluators
judge-llm list reporters
```

### Basic Config Template
```yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini
    agent_id: my_agent

evaluators:
  - type: response_evaluator

reporters:
  - type: console
```
