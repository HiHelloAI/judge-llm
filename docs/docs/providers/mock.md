---
sidebar_position: 3
---

# Mock Provider

Test your evaluation framework without making real API calls or incurring costs.

## Overview

The **Mock Provider** is a built-in provider that simulates LLM responses without connecting to any external API. It's perfect for:

- 🧪 Testing evaluation logic
- 🚀 CI/CD pipelines
- 💰 Cost-free development
- ⚡ Fast iteration
- 🔒 Offline development

## How It Works

The Mock Provider simply returns the `final_response` from your evalset files as if they came from an LLM:

```
EvalCase → Mock Provider → Return expected response → Evaluators
```

**No API calls. No costs. Instant results.**

## Installation

The Mock Provider is **built-in** - no additional installation required!

```bash
pip install judge-llm  # Mock provider included
```

## Configuration

### Basic Configuration

```yaml
providers:
  - type: mock
    agent_id: test_agent
```

### Full Configuration

```yaml
providers:
  - type: mock
    agent_id: my_test_agent
    model: mock-model-v1  # Optional, for metadata only
```

That's it! No API keys, no additional setup.

## Usage Examples

### Example 1: Testing Evaluators

Perfect for developing custom evaluators without API costs:

```yaml
# config.yaml
dataset:
  loader: local_file
  paths: [./test_cases.json]

providers:
  - type: mock
    agent_id: test_agent

evaluators:
  - type: response_evaluator
    config: {similarity_threshold: 0.8}
  - type: cost_evaluator
    config: {max_cost_per_case: 0.0}  # Should be $0 with mock

reporters:
  - type: console
```

### Example 2: CI/CD Pipeline

Run tests in GitHub Actions without credentials:

```yaml
# .github/workflows/test.yml
name: Test Evaluations

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install
        run: pip install -e .
      - name: Run Tests
        run: judge-llm run --config ci-config.yaml
```

```yaml
# ci-config.yaml
providers:
  - type: mock  # No API keys needed!
    agent_id: ci_agent
```

### Example 3: Baseline Comparison

Use mock as baseline to compare against real providers:

```yaml
providers:
  - type: mock
    agent_id: baseline
    
  - type: gemini
    agent_id: gemini_test
    model: gemini-2.0-flash-exp
```

Compare how Gemini differs from expected responses.

## Mock Provider Behavior

### Response Source

Mock provider returns the `final_response` from your evalset:

```json
{
  "conversation": [
    {
      "user_content": {"parts": [{"text": "What is 2+2?"}]},
      "final_response": {"parts": [{"text": "4"}]}  // ← Mock returns this
    }
  ]
}
```

### Metadata

Mock provider generates realistic metadata:

```python
{
    "conversation_history": [...],  # Your expected responses
    "cost": 0.0,                    # Always $0
    "time_taken": 0.001,            # ~1ms (instant)
    "token_usage": {
        "input_tokens": 10,         # Estimated
        "output_tokens": 5,          # Estimated
        "total_tokens": 15
    },
    "success": True                  # Always succeeds
}
```

### Multi-Turn Conversations

Mock provider supports multi-turn conversations:

```json
{
  "conversation": [
    {
      "user_content": {"parts": [{"text": "Hi"}]},
      "final_response": {"parts": [{"text": "Hello!"}]}
    },
    {
      "user_content": {"parts": [{"text": "How are you?"}]},
      "final_response": {"parts": [{"text": "I'm well!"}]}
    }
  ]
}
```

Each turn's response is returned in sequence.

## When to Use Mock Provider

### ✅ Use Mock When:

- **Developing evaluators** - Test evaluation logic without API costs
- **Running CI/CD** - Automated tests in pipelines
- **Offline work** - No internet connection
- **Testing framework** - Validating configuration
- **Cost concerns** - Budget-conscious development
- **Quick iteration** - Fast feedback loops

### ❌ Don't Use Mock When:

- **Testing LLM quality** - Need real model responses
- **Production evaluation** - Assessing actual agent performance
- **Comparing providers** - Need real provider differences
- **Safety testing** - Need actual model behavior
- **A/B testing** - Comparing real model versions

## Comparison: Mock vs Real Providers

| Feature | Mock | Gemini | OpenAI |
|---------|------|--------|--------|
| **Cost** | $0 | ~$0.001/call | ~$0.002/call |
| **Speed** | 1ms | 500-2000ms | 800-3000ms |
| **API Key** | None | Required | Required |
| **Offline** | ✅ Yes | ❌ No | ❌ No |
| **Real Responses** | ❌ No | ✅ Yes | ✅ Yes |
| **Use Case** | Testing | Production | Production |

## Development Workflow

### Recommended Workflow

1. **Develop with Mock** 🧪
   ```yaml
   providers:
     - type: mock
       agent_id: dev_agent
   ```
   - Build evalsets
   - Develop evaluators
   - Test configuration

2. **Test with Small Batch** 🔬
   ```yaml
   providers:
     - type: gemini
       agent_id: test_agent
   ```
   - Run on 5-10 test cases
   - Verify costs
   - Check quality

3. **Production Evaluation** 🚀
   ```yaml
   providers:
     - type: gemini
       agent_id: prod_agent
   ```
   - Full test suite
   - Monitor costs
   - Generate reports

## Configuration Examples

### Example 1: Multiple Mock Agents

Test different agent configurations:

```yaml
providers:
  - type: mock
    agent_id: agent_v1
    model: mock-v1
    
  - type: mock
    agent_id: agent_v2
    model: mock-v2
```

### Example 2: Mixed Providers

Combine mock and real providers:

```yaml
providers:
  - type: mock
    agent_id: baseline
    
  - type: gemini
    agent_id: production
    model: gemini-2.0-flash-exp
```

### Example 3: Programmatic API

```python
from judge_llm import evaluate

# Development with mock
dev_report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "mock", "agent_id": "dev"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "console"}]
)

print(f"Dev tests passed: {dev_report.success_rate == 1.0}")
print(f"Cost: ${dev_report.total_cost}")  # Always $0
```

## Troubleshooting

### Responses Not Matching

**Issue:** Evaluators failing with mock provider

**Cause:** Expected responses in evalset don't match evaluation criteria

**Solution:** Check your evalset's `final_response` matches what evaluators expect

### Always 100% Success Rate

**Expected Behavior:** Mock provider always succeeds since it returns exactly what you defined

**This is correct!** Mock provider is for testing the framework, not the agent.

## Best Practices

### 1. Development First

Always start development with mock provider:
- Build evalsets
- Test evaluators
- Validate configuration
- No API costs!

### 2. Gradual Transition

Move to real providers gradually:
1. Mock for initial development
2. Small batch with real provider
3. Full evaluation in production

### 3. CI/CD Integration

Use mock in automated tests:
```yaml
# .github/workflows/test.yml
- name: Run Evaluation Tests
  run: judge-llm run --config ci-config.yaml
  # ci-config.yaml uses mock provider
```

### 4. Cost Estimation

Use mock to estimate test suite size, then calculate real provider costs:
```
Mock: 100 tests in 0.1s, $0
Gemini estimate: 100 tests × $0.001 = $0.10
```

## Related Documentation

- [Providers Overview](./overview.md)
- [Gemini Provider](./gemini.md)
- [Custom Providers](./custom-providers.md)
- [Quick Start](../quick-start.md) - Uses mock provider

## API Reference

For implementation details, see the [MockProvider API Reference](../api-reference/base-classes.md#mockprovider).
