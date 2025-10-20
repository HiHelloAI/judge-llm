---
sidebar_position: 2
---

# Gemini Provider

The Gemini Provider integrates Google's Gemini models into Judge LLM, allowing you to evaluate and compare different Gemini model variants systematically.

## Overview

**Type:** `gemini`

**Purpose:** Execute evaluations using Google's Gemini family of models via the official Gemini API.

**Key Features:**
- ✅ Multiple Gemini models supported
- ✅ Cost tracking per request
- ✅ Token usage monitoring
- ✅ Multi-turn conversations
- ✅ Tool calling support
- ✅ Streaming support
- ✅ Safety settings configuration

## Quick Start

### Basic Configuration

```yaml
providers:
  - type: gemini
    agent_id: my_gemini_agent
    model: gemini-2.0-flash-exp
    api_key: ${GOOGLE_API_KEY}
```

### Environment Setup

1. **Get API Key:**
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Create or select a project
   - Generate an API key

2. **Add to .env:**
   ```bash
   GOOGLE_API_KEY=your-api-key-here
   ```

3. **Run Evaluation:**
   ```bash
   judge-llm run --config config.yaml
   ```

## Configuration Options

### Complete Configuration

```yaml
providers:
  - type: gemini
    agent_id: gemini_agent

    # Model Selection
    model: gemini-2.0-flash-exp

    # Generation Parameters
    temperature: 1.0
    max_tokens: 8192
    top_p: 0.95
    top_k: 40

    # Authentication
    api_key: ${GOOGLE_API_KEY}
```

### Configuration Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | string | - | Must be `gemini` |
| `agent_id` | string | - | Unique identifier for this configuration |
| `model` | string | `gemini-2.0-flash-exp` | Gemini model to use |
| `temperature` | float | `1.0` | Sampling temperature (0.0-2.0) |
| `max_tokens` | int | `8192` | Maximum response tokens |
| `top_p` | float | `0.95` | Top-p (nucleus) sampling |
| `top_k` | int | `40` | Top-k sampling |
| `api_key` | string | `${GOOGLE_API_KEY}` | Google API key |

## Supported Models

### Production Models

```yaml
# Latest experimental model (recommended)
model: gemini-2.0-flash-exp

# Stable flash model (fast & cost-effective)
model: gemini-1.5-flash

# High capability model
model: gemini-1.5-pro

# Ultra-fast, lightweight model
model: gemini-1.5-flash-8b
```

### Model Comparison

| Model | Speed | Cost | Capability | Best For |
|-------|-------|------|------------|----------|
| `gemini-2.0-flash-exp` | ⚡⚡⚡ Fast | 💰 Low | 🎯 High | Latest features, experimentation |
| `gemini-1.5-flash` | ⚡⚡⚡ Fast | 💰 Low | 🎯 Good | Production, high throughput |
| `gemini-1.5-pro` | ⚡⚡ Medium | 💰💰 Medium | 🎯🎯 Excellent | Complex tasks, high quality |
| `gemini-1.5-flash-8b` | ⚡⚡⚡⚡ Ultra Fast | 💰 Very Low | 🎯 Basic | Simple tasks, extreme throughput |

## Generation Parameters

### Temperature

Controls randomness in responses:

```yaml
# Deterministic (good for testing)
temperature: 0.0

# Balanced (default)
temperature: 1.0

# Creative
temperature: 1.5
```

**Recommendations:**
- Use `0.0` for consistent evaluation results
- Use `0.7-1.0` for balanced responses
- Use `1.0-2.0` for creative tasks

### Max Tokens

Limits response length:

```yaml
# Short responses
max_tokens: 512

# Default
max_tokens: 8192

# Maximum (model dependent)
max_tokens: 32768  # For pro models
```

### Top-P and Top-K

Control response diversity:

```yaml
# More focused
top_p: 0.8
top_k: 20

# Default (balanced)
top_p: 0.95
top_k: 40

# More diverse
top_p: 1.0
top_k: 64
```

## Cost Tracking

The Gemini Provider automatically tracks API costs:

### Viewing Costs

```python
from judge_llm import evaluate

report = evaluate(config="config.yaml")

# Total cost across all runs
print(f"Total cost: ${report.total_cost:.4f}")

# Per-run costs
for run in report.execution_runs:
    cost = run.provider_result.cost
    tokens = run.provider_result.token_usage
    print(f"{run.eval_case_id}: ${cost:.4f} ({tokens['total_tokens']} tokens)")
```

### Cost Optimization

```yaml
evaluators:
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.05  # Alert if cost > $0.05 per test
```

## Token Usage

Monitor token consumption:

```python
for run in report.execution_runs:
    tokens = run.provider_result.token_usage
    print(f"Prompt tokens: {tokens.get('prompt_tokens', 0)}")
    print(f"Completion tokens: {tokens.get('completion_tokens', 0)}")
    print(f"Total tokens: {tokens.get('total_tokens', 0)}")
```

## Multi-turn Conversations

The Gemini Provider supports multi-turn conversations with context:

```yaml
# evalset.yaml
eval_cases:
  - eval_id: multi_turn_test
    conversation:
      # Turn 1
      - invocation_id: turn_1
        user_content:
          parts:
            - text: "What is the capital of France?"
        final_response:
          parts:
            - text: "The capital of France is Paris."

      # Turn 2 (with context from turn 1)
      - invocation_id: turn_2
        user_content:
          parts:
            - text: "What is its population?"
        final_response:
          parts:
            - text: "Paris has a population of approximately 2.2 million."
```

## Advanced Configuration

### Comparing Different Models

```yaml
providers:
  # Fast model for high volume
  - type: gemini
    agent_id: gemini_flash
    model: gemini-2.0-flash-exp
    temperature: 0.0
    max_tokens: 512

  # High quality for complex tasks
  - type: gemini
    agent_id: gemini_pro
    model: gemini-1.5-pro
    temperature: 0.7
    max_tokens: 4096
```

### Different Temperatures

```yaml
providers:
  # Deterministic baseline
  - type: gemini
    agent_id: baseline_temp0
    temperature: 0.0

  # Creative variant
  - type: gemini
    agent_id: creative_temp1_5
    temperature: 1.5
```

## Error Handling

The provider handles common errors gracefully:

```python
# Errors are captured in provider results
for run in report.execution_runs:
    if not run.provider_result.success:
        print(f"Error in {run.eval_case_id}:")
        print(f"  {run.provider_result.error}")
```

Common errors:
- **API Key Invalid** - Check `GOOGLE_API_KEY` in `.env`
- **Rate Limit** - Add delays between requests
- **Model Not Found** - Check model name spelling
- **Quota Exceeded** - Check Google Cloud quotas

## Performance Tips

### 1. Use Parallel Execution

```yaml
agent:
  parallel_execution: true
  max_workers: 4  # Adjust based on rate limits
```

### 2. Choose Appropriate Models

```yaml
# For simple classification
model: gemini-1.5-flash-8b

# For complex reasoning
model: gemini-1.5-pro
```

### 3. Optimize Token Usage

```yaml
# Limit response length
max_tokens: 512  # Instead of default 8192

# Use lower temperature for consistency
temperature: 0.0
```

## Examples

### Example 1: Basic Evaluation

```yaml
# config.yaml
agent:
  num_runs: 1

dataset:
  loader: local_file
  paths: [./tests.yaml]

providers:
  - type: gemini
    agent_id: gemini_flash
    model: gemini-2.0-flash-exp

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.85
```

### Example 2: Model Comparison

```yaml
providers:
  # Compare flash vs pro
  - type: gemini
    agent_id: flash
    model: gemini-2.0-flash-exp

  - type: gemini
    agent_id: pro
    model: gemini-1.5-pro

# Both will run on the same test cases
```

### Example 3: Temperature Tuning

```yaml
providers:
  - type: gemini
    agent_id: temp_0_0
    temperature: 0.0

  - type: gemini
    agent_id: temp_0_7
    temperature: 0.7

  - type: gemini
    agent_id: temp_1_5
    temperature: 1.5
```

## Troubleshooting

### API Key Not Found

```bash
# Check .env file exists
ls -la .env

# Verify GOOGLE_API_KEY is set
echo $GOOGLE_API_KEY

# Load .env manually if needed
export $(cat .env | xargs)
```

### Rate Limiting

```yaml
# Reduce parallel workers
agent:
  parallel_execution: true
  max_workers: 2  # Reduced from 4
```

### High Costs

```yaml
# Add cost evaluator
evaluators:
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.01  # Alert on expensive tests
```

## API Reference

See the [Gemini API documentation](https://ai.google.dev/docs) for:
- Model capabilities
- Pricing information
- Rate limits
- API updates

## Related Documentation

- [Providers Overview](./overview) - All provider types
- [Configuration Guide](../guides/configuration#gemini-provider) - Detailed config
- [Examples](../examples/gemini-agent) - Working example
- [Python API](../guides/python-api) - Programmatic usage

## Next Steps

- [Mock Provider](./mock-provider) - Test without API calls
- [Google ADK Provider](./google-adk-provider) - Build agents
- [Custom Providers](./custom-providers) - Implement other LLMs
