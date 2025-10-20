---
sidebar_position: 5
---

# Custom Providers

Create custom providers to integrate any LLM service (OpenAI, Anthropic, Azure, local models, etc.) into Judge LLM.

## Overview

Custom providers allow you to:
- ✅ Integrate any LLM API
- ✅ Support local models
- ✅ Implement custom logic
- ✅ Use with all evaluators
- ✅ Register globally for reuse

## Quick Start

### 1. Implement BaseProvider

```python
# my_providers/openai_provider.py
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult, Invocation, Content, Part
import openai

class OpenAIProvider(BaseProvider):
    def __init__(self, agent_id, agent_config_path=None, agent_metadata=None, **provider_metadata):
        super().__init__(agent_id, agent_config_path, agent_metadata, **provider_metadata)

        # Get custom config
        self.model = provider_metadata.get("model", "gpt-4")
        self.api_key = provider_metadata.get("api_key")
        self.temperature = provider_metadata.get("temperature", 0.7)

        # Initialize client
        self.client = openai.OpenAI(api_key=self.api_key)

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """Execute evaluation case using OpenAI."""
        try:
            # Build conversation history
            conversation_history = []

            for inv in eval_case.conversation:
                # Call OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user",
                        "content": inv.user_content.parts[0].text
                    }],
                    temperature=self.temperature
                )

                # Build result
                conversation_history.append(
                    Invocation(
                        invocation_id=inv.invocation_id,
                        user_content=inv.user_content,
                        final_response=Content(
                            parts=[Part(text=response.choices[0].message.content)],
                            role="assistant"
                        ),
                        intermediate_data=inv.intermediate_data,
                        creation_timestamp=inv.creation_timestamp
                    )
                )

            # Calculate cost (example)
            total_tokens = response.usage.total_tokens
            cost = total_tokens * 0.00003  # $0.03 per 1K tokens

            return ProviderResult(
                conversation_history=conversation_history,
                cost=cost,
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": total_tokens
                },
                metadata={
                    "provider": "openai",
                    "model": self.model
                },
                success=True
            )

        except Exception as e:
            return ProviderResult(
                conversation_history=[],
                success=False,
                error=str(e)
            )

    def cleanup(self):
        """Cleanup resources."""
        pass
```

### 2. Configure Provider

```yaml
providers:
  - type: custom
    module_path: ./my_providers/openai_provider.py
    class_name: OpenAIProvider
    agent_id: openai_agent
    # Custom config passed to __init__
    model: gpt-4
    api_key: ${OPENAI_API_KEY}
    temperature: 0.7
```

### 3. Run Evaluation

```bash
judge-llm run --config config.yaml
```

## BaseProvider Interface

All providers must implement:

```python
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult

class MyProvider(BaseProvider):
    def __init__(self, agent_id, agent_config_path=None, agent_metadata=None, **provider_metadata):
        """
        Args:
            agent_id: Unique identifier
            agent_config_path: Path to agent config (optional)
            agent_metadata: Provider-specific metadata
            **provider_metadata: Custom config from YAML
        """
        super().__init__(agent_id, agent_config_path, agent_metadata, **provider_metadata)

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """
        Execute evaluation case.

        Args:
            eval_case: Test case with conversation turns

        Returns:
            ProviderResult with conversation history and metrics
        """
        pass

    def cleanup(self):
        """Cleanup resources after evaluation."""
        pass
```

## Provider Examples

### Example 1: Anthropic Claude

```python
# my_providers/anthropic_provider.py
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult, Invocation, Content, Part
import anthropic

class AnthropicProvider(BaseProvider):
    def __init__(self, agent_id, **provider_metadata):
        super().__init__(agent_id, **provider_metadata)
        self.model = provider_metadata.get("model", "claude-3-5-sonnet-20241022")
        self.client = anthropic.Anthropic(api_key=provider_metadata.get("api_key"))

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        conversation_history = []

        for inv in eval_case.conversation:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": inv.user_content.parts[0].text
                }]
            )

            conversation_history.append(
                Invocation(
                    invocation_id=inv.invocation_id,
                    user_content=inv.user_content,
                    final_response=Content(
                        parts=[Part(text=response.content[0].text)],
                        role="assistant"
                    ),
                    intermediate_data=inv.intermediate_data,
                    creation_timestamp=inv.creation_timestamp
                )
            )

        return ProviderResult(
            conversation_history=conversation_history,
            cost=response.usage.input_tokens * 0.000003 + response.usage.output_tokens * 0.000015,
            token_usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            success=True
        )
```

### Example 2: Local Model (Ollama)

```python
# my_providers/ollama_provider.py
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult, Invocation, Content, Part
import requests

class OllamaProvider(BaseProvider):
    def __init__(self, agent_id, **provider_metadata):
        super().__init__(agent_id, **provider_metadata)
        self.model = provider_metadata.get("model", "llama2")
        self.endpoint = provider_metadata.get("endpoint", "http://localhost:11434")

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        conversation_history = []

        for inv in eval_case.conversation:
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": inv.user_content.parts[0].text
                }
            )

            result = response.json()

            conversation_history.append(
                Invocation(
                    invocation_id=inv.invocation_id,
                    user_content=inv.user_content,
                    final_response=Content(
                        parts=[Part(text=result["response"])],
                        role="assistant"
                    ),
                    intermediate_data=inv.intermediate_data,
                    creation_timestamp=inv.creation_timestamp
                )
            )

        return ProviderResult(
            conversation_history=conversation_history,
            cost=0.0,  # Local model - no cost
            success=True
        )
```

## Global Registration

Register providers once, use everywhere:

### In .judge_llm.defaults.yaml

```yaml
providers:
  - type: custom
    module_path: ./my_providers/openai_provider.py
    class_name: OpenAIProvider
    register_as: openai  # ← Register globally
```

### Use by Name

```yaml
# config.yaml
providers:
  - type: openai  # ← Uses registered provider
    agent_id: gpt4
    model: gpt-4
```

### Programmatic Registration

```python
from judge_llm import register_provider
from my_providers import OpenAIProvider

register_provider("openai", OpenAIProvider)
```

## Best Practices

### 1. Handle Errors Gracefully

```python
def execute(self, eval_case: EvalCase) -> ProviderResult:
    try:
        # Your implementation
        pass
    except Exception as e:
        return ProviderResult(
            conversation_history=[],
            success=False,
            error=str(e)  # Include error details
        )
```

### 2. Track Metrics

```python
return ProviderResult(
    conversation_history=history,
    cost=calculated_cost,  # Track API costs
    token_usage=tokens,     # Track token usage
    metadata={"model": self.model},  # Provider info
    success=True
)
```

### 3. Support Multi-turn

```python
def execute(self, eval_case: EvalCase) -> ProviderResult:
    conversation_history = []

    # Process each turn
    for inv in eval_case.conversation:
        # Call LLM
        response = self.call_llm(inv.user_content.parts[0].text)

        # Append to history
        conversation_history.append(...)

    return ProviderResult(conversation_history=conversation_history, ...)
```

### 4. Use Environment Variables

```python
def __init__(self, agent_id, **provider_metadata):
    super().__init__(agent_id, **provider_metadata)

    # Use env vars for sensitive data
    api_key = provider_metadata.get("api_key") or os.getenv("MY_API_KEY")
```

## Testing Your Provider

### 1. Unit Test

```python
# test_my_provider.py
from my_providers import MyProvider
from judge_llm.core.models import EvalCase, SessionInput, Invocation

def test_provider():
    provider = MyProvider(agent_id="test", model="test-model")

    eval_case = EvalCase(
        eval_id="test",
        session_input=SessionInput(app_name="test"),
        conversation=[...]
    )

    result = provider.execute(eval_case)

    assert result.success == True
    assert len(result.conversation_history) > 0
```

### 2. Integration Test

```yaml
# test-config.yaml
providers:
  - type: custom
    module_path: ./my_providers/my_provider.py
    class_name: MyProvider
    agent_id: test_agent
```

```bash
judge-llm run --config test-config.yaml
```

## Common Patterns

### Pattern 1: Stateless API

```python
def execute(self, eval_case: EvalCase) -> ProviderResult:
    # Each turn is independent
    for inv in eval_case.conversation:
        response = self.api_call(inv.user_content)
```

### Pattern 2: Stateful Conversation

```python
def execute(self, eval_case: EvalCase) -> ProviderResult:
    # Build full conversation history
    messages = []
    for inv in eval_case.conversation:
        messages.append({"role": "user", "content": inv.user_content})
        response = self.api_call(messages)
        messages.append({"role": "assistant", "content": response})
```

### Pattern 3: Batch Processing

```python
def execute(self, eval_case: EvalCase) -> ProviderResult:
    # Process all turns in one batch call
    all_prompts = [inv.user_content for inv in eval_case.conversation]
    responses = self.batch_api_call(all_prompts)
```

## Related Documentation

- [Providers Overview](./overview)
- [Gemini Provider](./gemini-provider) - Example implementation
- [Configuration Guide](../guides/configuration)
- [Python API](../guides/python-api)

## Next Steps

- See examples in `examples/custom_reporter_example/`
- Review [BaseProvider source code](https://github.com/yourusername/judge-llm/blob/main/judge_llm/providers/base.py)
- Check [Gemini Provider](./gemini-provider) as a reference implementation
