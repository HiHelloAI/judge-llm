---
sidebar_position: 1
---

# Providers Overview

Providers are the bridge between Judge LLM and actual LLM services. They execute your test cases against different LLM platforms and return results for evaluation.

## What are Providers?

A **Provider** is a component that:
- Connects to an LLM service (Gemini, OpenAI, Claude, etc.)
- Executes test cases by sending prompts
- Returns responses with metadata (cost, tokens, latency)
- Handles authentication and API calls

## Available Providers

### Built-in Providers

| Provider | Status | API Required | Use Case |
|----------|--------|--------------|----------|
| **[Mock](./mock.md)** | ✅ Ready | No | Testing, development, CI/CD |
| **[Gemini](./gemini.md)** | ✅ Ready | Yes | Google AI evaluation |
| **OpenAI** | 🚧 Coming Soon | Yes | GPT models evaluation |
| **Claude** | 🚧 Coming Soon | Yes | Anthropic models evaluation |

### Custom Providers

You can create [custom providers](./custom-providers.md) to integrate with:
- Internal LLM services
- Fine-tuned models
- Custom API endpoints
- Local model deployments

## How Providers Work

### 1. Configuration

Providers are configured in your `config.yaml`:

```yaml
providers:
  - type: gemini
    agent_id: my_agent
    model: gemini-2.0-flash-exp
    # Provider-specific options
```

### 2. Execution Flow

```
EvalCase → Provider → LLM API → Response → Evaluators
```

1. Provider receives test case
2. Formats prompt for LLM API
3. Calls the LLM service
4. Captures response + metadata
5. Returns structured result

### 3. Provider Result

Each provider returns a `ProviderResult` with:

```python
{
    "conversation_history": [...],  # All turns in conversation
    "cost": 0.0012,                 # API cost in USD
    "time_taken": 1.23,             # Latency in seconds
    "token_usage": {
        "input_tokens": 150,
        "output_tokens": 75,
        "total_tokens": 225
    },
    "success": True                 # Execution success
}
```

## Selecting a Provider

### Mock Provider - For Testing

✅ **Use when:**
- Testing your evaluation framework
- Running CI/CD without API costs
- Developing custom evaluators
- Validating configuration

❌ **Don't use when:**
- You need real LLM responses
- Testing actual model quality
- Production evaluations

### Gemini Provider - For Production

✅ **Use when:**
- Evaluating Google Gemini models
- Need fast, cost-effective evaluation
- Testing multi-modal capabilities
- Production quality assessment

**Requirements:**
- `GOOGLE_API_KEY` environment variable
- Google AI Studio account
- Internet connection

### Custom Providers - For Specific Needs

✅ **Use when:**
- Testing internal LLM services
- Evaluating fine-tuned models
- Need custom authentication
- Working with local deployments

## Provider Metadata

All providers include metadata in their results:

| Field | Description | Example |
|-------|-------------|---------|
| `agent_id` | Identifier for the agent | `"my_agent"` |
| `model` | Model name/version | `"gemini-2.0-flash-exp"` |
| `provider_type` | Provider type | `"gemini"` |
| `config` | Provider configuration | `{...}` |

## Best Practices

### 1. Environment Variables

Always use environment variables for API keys:

```bash
# .env file
GOOGLE_API_KEY=your-key-here
```

Never hardcode keys in config files!

### 2. Cost Tracking

Monitor costs across evaluations:

```yaml
evaluators:
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.10  # $0.10 limit per test
```

### 3. Error Handling

Providers handle errors gracefully:
- Network timeouts
- API rate limits
- Invalid responses
- Authentication failures

Check `success` field in results.

### 4. Parallel Execution

Run multiple test cases in parallel:

```yaml
agent:
  parallel_execution: true
  max_workers: 4  # Concurrent API calls
```

## Next Steps

- [Setup Mock Provider](./mock.md) - Test without API costs
- [Configure Gemini](./gemini.md) - Use Google Gemini
- [Create Custom Provider](./custom-providers.md) - Build your own
- [API Reference](/docs/api-reference/base-classes) - Provider interface

## Common Questions

**Q: Can I use multiple providers in one evaluation?**  
A: Yes! Configure multiple providers to compare results:

```yaml
providers:
  - type: gemini
    agent_id: agent_gemini
    model: gemini-2.0-flash-exp
  - type: mock
    agent_id: agent_baseline
```

**Q: How are costs calculated?**  
A: Each provider implements cost tracking based on their API pricing. See [Gemini Provider](./gemini.md#cost-tracking) for details.

**Q: Can I test offline?**  
A: Yes, use the [Mock Provider](./mock.md) which requires no network connection.
