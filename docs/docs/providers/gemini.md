---
sidebar_position: 2
---

# Gemini Provider

Evaluate your AI agents using Google's Gemini models - fast, cost-effective, and production-ready.

## Overview

The Gemini provider connects to Google's Gemini API to execute your test cases against state-of-the-art language models.

**Key Features:**
- ✅ Multiple Gemini models (Flash, Pro)
- ✅ Automatic cost tracking
- ✅ Token usage monitoring
- ✅ Multi-turn conversation support
- ✅ Configurable parameters (temperature, max_tokens, etc.)

## Installation

```bash
pip install judge-llm[gemini]
```

This installs the `google-genai` package required for Gemini API access.

## API Key Setup

### 1. Get Your API Key

Visit [Google AI Studio](https://ai.google.dev/) and create an API key.

### 2. Configure Environment Variable

Add to your `.env` file:

```bash
GOOGLE_API_KEY=your-api-key-here
```

Or set as environment variable:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

The framework automatically loads `.env` files on startup.

## Configuration

### Basic Configuration

```yaml
providers:
  - type: gemini
    agent_id: my_agent
    model: gemini-2.0-flash-exp
```

### Full Configuration

```yaml
providers:
  - type: gemini
    agent_id: my_gemini_agent
    model: gemini-2.0-flash-exp
    
    # Model parameters
    temperature: 0.7
    max_tokens: 2048
    top_p: 0.95
    top_k: 40
    
    # Optional: Override API key (not recommended)
    # api_key: ${GOOGLE_API_KEY}  # Use env var instead
```

## Available Models

| Model | Best For | Speed | Cost | Context |
|-------|----------|-------|------|---------|
| `gemini-2.0-flash-exp` | Fast evaluation | ⚡⚡⚡ | 💰 | 1M tokens |
| `gemini-1.5-pro` | Complex reasoning | ⚡⚡ | 💰💰 | 2M tokens |
| `gemini-1.5-flash` | Balanced | ⚡⚡⚡ | 💰 | 1M tokens |

### Model Selection Guide

**gemini-2.0-flash-exp** (Recommended)
- Fastest response times
- Most cost-effective
- Great for most evaluation tasks
- Experimental features

**gemini-1.5-pro**
- Best for complex reasoning
- Higher quality responses
- More expensive
- Use for critical evaluations

**gemini-1.5-flash**
- Balanced performance
- Good for production
- Stable (non-experimental)

## Configuration Parameters

### temperature (float, 0.0-2.0)

Controls randomness in responses:

```yaml
temperature: 0.7  # Default
```

- `0.0` - Deterministic, focused
- `0.7` - Balanced (recommended)
- `1.5+` - Creative, varied

### max_tokens (int)

Maximum tokens in response:

```yaml
max_tokens: 2048  # Default
```

Limits response length and cost.

### top_p (float, 0.0-1.0)

Nucleus sampling threshold:

```yaml
top_p: 0.95  # Default
```

Controls diversity of word selection.

### top_k (int)

Top-k sampling parameter:

```yaml
top_k: 40  # Default
```

Limits vocabulary to top K tokens.

## Cost Tracking

The Gemini provider automatically tracks costs based on Google's pricing.

### Current Pricing (as of 2025)

**Input Tokens:**
- Free tier: First 1M tokens/day
- Paid: $0.00025 per 1K tokens

**Output Tokens:**
- Free tier: First 100K tokens/day
- Paid: $0.0005 per 1K tokens

### Viewing Costs

Costs appear in all reports:

```bash
Total cost: $0.001234
Cost per case: $0.000412
```

### Cost Limits

Set maximum cost per test case:

```yaml
evaluators:
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.10  # $0.10 limit
```

## Usage Examples

### Example 1: Basic Evaluation

```yaml
# config.yaml
dataset:
  loader: local_file
  paths: [./my_test.json]

providers:
  - type: gemini
    agent_id: my_agent
    model: gemini-2.0-flash-exp

evaluators:
  - type: response_evaluator

reporters:
  - type: console
```

Run:
```bash
judge-llm run --config config.yaml
```

### Example 2: Programmatic Usage

```python
from judge_llm import evaluate

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./test.json"]},
    providers=[{
        "type": "gemini",
        "agent_id": "my_agent",
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.7
    }],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "console"}]
)

print(f"Cost: ${report.total_cost:.4f}")
print(f"Success: {report.success_rate:.1%}")
```

### Example 3: Multiple Gemini Agents

Compare different Gemini configurations:

```yaml
providers:
  - type: gemini
    agent_id: agent_creative
    model: gemini-2.0-flash-exp
    temperature: 1.2
    
  - type: gemini
    agent_id: agent_focused
    model: gemini-2.0-flash-exp
    temperature: 0.1
```

## Multi-Turn Conversations

Gemini provider supports multi-turn conversations natively:

```json
{
  "conversation": [
    {
      "user_content": {"parts": [{"text": "Hello"}]},
      "final_response": {"parts": [{"text": "Hi!"}]}
    },
    {
      "user_content": {"parts": [{"text": "How are you?"}]},
      "final_response": {"parts": [{"text": "I'm well!"}]}
    }
  ]
}
```

The provider maintains conversation context automatically.

## Troubleshooting

### API Key Not Found

**Error:** `GOOGLE_API_KEY environment variable not set`

**Solution:**
1. Check `.env` file exists in project root
2. Verify key is set: `echo $GOOGLE_API_KEY`
3. Restart terminal/IDE after setting

### Rate Limiting

**Error:** `429 Too Many Requests`

**Solutions:**
- Reduce `max_workers` in config
- Add delays between requests
- Check API quota limits
- Upgrade API plan

### Invalid Model Name

**Error:** `Model not found: gemini-x.x`

**Solution:**
Use valid model names:
- `gemini-2.0-flash-exp`
- `gemini-1.5-pro`
- `gemini-1.5-flash`

### Cost Concerns

**Issue:** Unexpected costs

**Solutions:**
- Use `cost_evaluator` to set limits
- Start with small test sets
- Use mock provider for development
- Monitor costs in dashboard

## Best Practices

### 1. Development vs Production

```yaml
# Development (use mock)
providers:
  - type: mock
    agent_id: dev_agent

# Production (use Gemini)
providers:
  - type: gemini
    agent_id: prod_agent
```

### 2. Cost Optimization

- Use `gemini-2.0-flash-exp` for most tasks
- Set `max_tokens` appropriately
- Use parallel execution wisely
- Monitor costs with evaluators

### 3. Quality Assurance

- Test with small batches first
- Compare against mock baseline
- Use multiple temperature settings
- Track success rates over time

### 4. Security

- Never commit API keys
- Use `.env` files
- Rotate keys regularly
- Set up billing alerts

## Complete Example

See the [Gemini Agent Example](../examples/gemini-agent.md) for a full walkthrough with:
- Real API calls
- Cost tracking
- Multiple test cases
- HTML report generation

## Related Documentation

- [Providers Overview](./overview.md)
- [Mock Provider](./mock.md)
- [Custom Providers](./custom-providers.md)
- [Cost Evaluator](../evaluators/cost-evaluator.md)

## API Reference

For implementation details, see the [GeminiProvider API Reference](../api-reference/base-classes.md#geminiprovider).
