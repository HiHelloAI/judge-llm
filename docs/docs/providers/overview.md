---
sidebar_position: 1
---

# Providers Overview

Providers are the LLM backends that Judge LLM evaluates. Each provider implements the interface to a specific LLM service or agent framework, allowing you to test and compare different models systematically.

## What is a Provider?

A provider is responsible for:
- **Executing test cases** against an LLM or agent
- **Managing conversations** with the model
- **Tracking metrics** like cost, latency, and token usage
- **Returning results** in a standardized format for evaluation

## Available Providers

Judge LLM includes several built-in providers and supports custom implementations:

### Built-in Providers

| Provider | Description | Use Case |
|----------|-------------|----------|
| **[Gemini](./gemini-provider)** | Google's Gemini models | Production LLM evaluation |
| **[Mock](./mock-provider)** | Test provider (no API calls) | Testing & development |
| **[Google ADK](./google-adk-provider)** | Google Agent Development Kit | AI agents with tool use |
| **[Custom](./custom-providers)** | Your own implementation | Any LLM service |

### Provider Comparison

| Feature | Gemini | Mock | Google ADK | Custom |
|---------|--------|------|------------|--------|
| API Calls | ✅ Yes | ❌ No | ✅ Yes | Depends |
| Cost Tracking | ✅ Yes | ✅ Simulated | ✅ Yes | Optional |
| Tool Calling | ✅ Yes | ❌ No | ✅ Yes | Optional |
| Authentication | ✅ API Key | ❌ None | ✅ API Key | Depends |
| Multi-turn | ✅ Yes | ✅ Yes | ✅ Yes | Optional |

## Quick Start

### Basic Configuration

```yaml
providers:
  - type: gemini
    agent_id: my_gemini_agent
    model: gemini-2.0-flash-exp
```

### Multiple Providers (A/B Testing)

```yaml
providers:
  - type: gemini
    agent_id: gemini_flash
    model: gemini-2.0-flash-exp

  - type: gemini
    agent_id: gemini_pro
    model: gemini-1.5-pro

  - type: mock
    agent_id: baseline
```

## Provider Interface

All providers implement the same interface:

```python
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult

class MyProvider(BaseProvider):
    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """Execute evaluation case and return results."""
        pass

    def cleanup(self):
        """Cleanup resources after evaluation."""
        pass
```

## Common Configuration

### Required Fields

All providers require these fields:

```yaml
providers:
  - type: <provider_type>  # Provider identifier
    agent_id: <unique_id>  # Your unique name for this configuration
```

### Optional Metadata

Pass custom configuration to providers:

```yaml
providers:
  - type: gemini
    agent_id: my_agent
    # Custom fields passed to provider
    temperature: 0.7
    max_tokens: 2048
    custom_setting: value
```

## Provider Registry

### Using Registered Providers

Register providers once in `.judge_llm.defaults.yaml`:

```yaml
providers:
  - type: custom
    module_path: ./my_providers/anthropic.py
    class_name: AnthropicProvider
    register_as: anthropic  # ← Register globally

# Then use by name in test configs
providers:
  - type: anthropic  # ← Use registered provider
    agent_id: claude
```

### Programmatic Registration

```python
from judge_llm import register_provider
from my_providers import MyProvider

register_provider("my_provider", MyProvider)
```

## Choosing a Provider

### For Development & Testing
- Use **[Mock Provider](./mock-provider)** - No API costs, instant execution

### For Production LLM Testing
- Use **[Gemini Provider](./gemini-provider)** - Google's production models

### For AI Agents with Tools
- Use **[Google ADK Provider](./google-adk-provider)** - Full agent capabilities

### For Other LLM Services
- Implement **[Custom Provider](./custom-providers)** - OpenAI, Anthropic, etc.

## Cost & Performance

### Cost Tracking

Providers automatically track costs when available:

```python
report = evaluate(config="config.yaml")
print(f"Total cost: ${report.total_cost:.4f}")
```

### Performance Metrics

All providers track execution time:

```python
for run in report.execution_runs:
    print(f"Provider: {run.provider_type}")
    print(f"Time: {run.provider_result.time_taken:.2f}s")
    print(f"Cost: ${run.provider_result.cost:.4f}")
```

## Provider Results

### Standard Output Format

All providers return results in the same format:

```python
ProviderResult(
    conversation_history=[...],  # Multi-turn conversations
    cost=0.0234,                # API cost in dollars
    time_taken=1.23,            # Execution time in seconds
    token_usage={               # Token counts
        "prompt_tokens": 150,
        "completion_tokens": 50,
        "total_tokens": 200
    },
    metadata={},                # Provider-specific metadata
    success=True,               # Execution status
    error=None                  # Error message if failed
)
```

## Best Practices

### 1. Use Consistent Agent IDs
```yaml
# Good - Clear, descriptive IDs
providers:
  - type: gemini
    agent_id: gemini_flash_2025
  - type: gemini
    agent_id: gemini_pro_2025

# Avoid - Generic IDs
providers:
  - type: gemini
    agent_id: agent1
  - type: gemini
    agent_id: agent2
```

### 2. Environment Variables for API Keys
```yaml
providers:
  - type: gemini
    agent_id: my_agent
    api_key: ${GOOGLE_API_KEY}  # ✅ From .env file
    # api_key: "hardcoded"      # ❌ Never hardcode keys
```

### 3. Provider-Specific Configs
```yaml
# Separate configs for different models
providers:
  - type: gemini
    agent_id: fast_cheap
    model: gemini-2.0-flash-exp
    temperature: 0.0
    max_tokens: 512

  - type: gemini
    agent_id: high_quality
    model: gemini-1.5-pro
    temperature: 0.7
    max_tokens: 4096
```

### 4. Start with Mock Provider
```yaml
# Test your evaluation logic first
providers:
  - type: mock
    agent_id: test_baseline

# Then switch to real provider
# providers:
#   - type: gemini
#     agent_id: production
```

## Next Steps

- **[Gemini Provider](./gemini-provider)** - Configure Google's Gemini models
- **[Mock Provider](./mock-provider)** - Set up test provider
- **[Google ADK Provider](./google-adk-provider)** - Build AI agents
- **[Custom Providers](./custom-providers)** - Implement your own

## Related Documentation

- [Configuration Guide](../guides/configuration) - Complete config reference
- [Python API](../guides/python-api) - Programmatic usage
- [Examples](../examples/overview) - Working examples
