---
sidebar_position: 4
---

# Custom Providers

Create custom providers to integrate Judge LLM with any LLM service or API.

## Overview

Custom providers allow you to evaluate agents using:
- Internal LLM services
- Fine-tuned models
- Local model deployments
- Custom API endpoints
- Proprietary systems

## Creating a Custom Provider

### Step 1: Inherit from BaseProvider

```python
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult, Content, Part

class MyCustomProvider(BaseProvider):
    def __init__(self, provider_metadata: dict):
        super().__init__(provider_metadata)
        # Initialize your provider
        self.api_endpoint = provider_metadata.get("api_endpoint")
        self.api_key = provider_metadata.get("api_key")
        
    def execute(self, eval_case: EvalCase) -> ProviderResult:
        # Implement your execution logic
        pass
        
    def cleanup(self):
        # Clean up resources
        pass
```

### Step 2: Implement execute() Method

The `execute()` method is where you call your LLM:

```python
def execute(self, eval_case: EvalCase) -> ProviderResult:
    import time
    import requests
    
    start_time = time.time()
    conversation_history = []
    total_cost = 0.0
    total_tokens = 0
    
    # Process each turn in the conversation
    for invocation in eval_case.conversation:
        # Extract user prompt
        user_prompt = invocation.user_content.parts[0].text
        
        # Call your LLM API
        response = requests.post(
            self.api_endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "prompt": user_prompt,
                "model": self.model,
                # Add your API parameters
            }
        )
        
        # Parse response
        data = response.json()
        agent_response = data["response"]
        tokens = data.get("tokens", 0)
        cost = data.get("cost", 0.0)
        
        # Build conversation history
        conversation_history.append({
            "user_content": invocation.user_content,
            "final_response": Content(
                parts=[Part(text=agent_response)],
                role="assistant"
            ),
            "invocation_id": invocation.invocation_id,
            "creation_timestamp": time.time()
        })
        
        total_cost += cost
        total_tokens += tokens
    
    # Return ProviderResult
    return ProviderResult(
        conversation_history=conversation_history,
        cost=total_cost,
        time_taken=time.time() - start_time,
        token_usage={
            "input_tokens": total_tokens // 2,
            "output_tokens": total_tokens // 2,
            "total_tokens": total_tokens
        },
        success=True
    )
```

### Step 3: Implement cleanup() Method

```python
def cleanup(self):
    """Clean up resources (connections, files, etc.)"""
    if hasattr(self, 'connection'):
        self.connection.close()
```

## Registration Methods

### Method 1: File-Based Registration

Create a Python file with your provider:

```python
# my_providers/custom_llm.py
from judge_llm.providers.base import BaseProvider

class CustomLLMProvider(BaseProvider):
    # Implementation here
    pass
```

Use in config:

```yaml
providers:
  - type: custom
    module_path: ./my_providers/custom_llm.py
    class_name: CustomLLMProvider
    agent_id: my_custom_agent
    
    # Custom configuration
    api_endpoint: https://api.example.com/generate
    api_key: ${CUSTOM_API_KEY}
    model: my-model-v1
```

### Method 2: Programmatic Registration

```python
from judge_llm import register_provider, evaluate
from my_providers.custom_llm import CustomLLMProvider

# Register your provider
register_provider("my_custom_llm", CustomLLMProvider)

# Use in evaluation
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{
        "type": "my_custom_llm",
        "agent_id": "custom_agent",
        "api_endpoint": "https://api.example.com",
        "api_key": "your-key"
    }],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "console"}]
)
```

## Complete Example

### Example 1: Local Model Provider

```python
# providers/local_model.py
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult, Content, Part
import time

class LocalModelProvider(BaseProvider):
    """Provider for locally hosted models (e.g., via Ollama)"""
    
    def __init__(self, provider_metadata: dict):
        super().__init__(provider_metadata)
        self.endpoint = provider_metadata.get("endpoint", "http://localhost:11434")
        self.model = provider_metadata.get("model", "llama2")
        
    def execute(self, eval_case: EvalCase) -> ProviderResult:
        import requests
        
        start_time = time.time()
        conversation_history = []
        
        for invocation in eval_case.conversation:
            user_text = invocation.user_content.parts[0].text
            
            # Call local model API
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": user_text,
                    "stream": False
                },
                timeout=30
            )
            
            result = response.json()
            agent_response = result.get("response", "")
            
            conversation_history.append({
                "user_content": invocation.user_content,
                "final_response": Content(
                    parts=[Part(text=agent_response)],
                    role="assistant"
                ),
                "invocation_id": invocation.invocation_id,
                "creation_timestamp": time.time()
            })
        
        return ProviderResult(
            conversation_history=conversation_history,
            cost=0.0,  # Local models are free
            time_taken=time.time() - start_time,
            token_usage={
                "total_tokens": len(user_text.split()) * 2  # Rough estimate
            },
            success=True
        )
    
    def cleanup(self):
        pass  # No cleanup needed
```

**Configuration:**

```yaml
providers:
  - type: custom
    module_path: ./providers/local_model.py
    class_name: LocalModelProvider
    agent_id: local_llama
    endpoint: http://localhost:11434
    model: llama2
```

### Example 2: REST API Provider

```python
# providers/rest_api.py
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult, Content, Part
import requests
import time

class RestAPIProvider(BaseProvider):
    """Generic REST API provider"""
    
    def __init__(self, provider_metadata: dict):
        super().__init__(provider_metadata)
        self.api_url = provider_metadata["api_url"]
        self.headers = {
            "Authorization": f"Bearer {provider_metadata.get('api_key')}",
            "Content-Type": "application/json"
        }
        
    def execute(self, eval_case: EvalCase) -> ProviderResult:
        start_time = time.time()
        conversation_history = []
        total_cost = 0.0
        
        for invocation in eval_case.conversation:
            user_text = invocation.user_content.parts[0].text
            
            # Make API call
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"input": user_text},
                timeout=30
            )
            
            if response.status_code != 200:
                return ProviderResult(
                    conversation_history=[],
                    cost=0.0,
                    time_taken=time.time() - start_time,
                    success=False,
                    error=f"API error: {response.status_code}"
                )
            
            data = response.json()
            agent_response = data.get("output", "")
            cost = data.get("cost", 0.0)
            
            conversation_history.append({
                "user_content": invocation.user_content,
                "final_response": Content(
                    parts=[Part(text=agent_response)],
                    role="assistant"
                ),
                "invocation_id": invocation.invocation_id,
                "creation_timestamp": time.time()
            })
            
            total_cost += cost
        
        return ProviderResult(
            conversation_history=conversation_history,
            cost=total_cost,
            time_taken=time.time() - start_time,
            success=True
        )
    
    def cleanup(self):
        pass
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def execute(self, eval_case: EvalCase) -> ProviderResult:
    try:
        # Your implementation
        return ProviderResult(...)
    except requests.RequestException as e:
        return ProviderResult(
            conversation_history=[],
            cost=0.0,
            time_taken=0.0,
            success=False,
            error=str(e)
        )
```

### 2. Cost Tracking

Implement accurate cost calculation:

```python
def _calculate_cost(self, tokens: int) -> float:
    """Calculate cost based on your pricing"""
    input_cost_per_1k = 0.001
    output_cost_per_1k = 0.002
    
    input_tokens = tokens // 2
    output_tokens = tokens // 2
    
    return (input_tokens / 1000 * input_cost_per_1k + 
            output_tokens / 1000 * output_cost_per_1k)
```

### 3. Timeout Handling

Always set timeouts:

```python
response = requests.post(
    url,
    json=data,
    timeout=30  # 30 second timeout
)
```

### 4. Logging

Add logging for debugging:

```python
from judge_llm.utils.logger import get_logger

class MyProvider(BaseProvider):
    def __init__(self, provider_metadata: dict):
        super().__init__(provider_metadata)
        self.logger = get_logger()
        
    def execute(self, eval_case: EvalCase) -> ProviderResult:
        self.logger.info(f"Executing test case: {eval_case.eval_id}")
        # Implementation
```

## Common Use Cases

### Use Case 1: Internal LLM Service

Connect to your company's internal LLM:

```python
class InternalLLMProvider(BaseProvider):
    def __init__(self, provider_metadata: dict):
        super().__init__(provider_metadata)
        self.internal_endpoint = provider_metadata["endpoint"]
        # Add internal auth, VPN, etc.
```

### Use Case 2: Fine-Tuned Model

Evaluate your fine-tuned model:

```python
class FineTunedProvider(BaseProvider):
    def __init__(self, provider_metadata: dict):
        super().__init__(provider_metadata)
        self.model_id = provider_metadata["model_id"]
        self.version = provider_metadata.get("version", "latest")
```

### Use Case 3: Cached Responses

Provider that caches responses:

```python
import hashlib
import json

class CachedProvider(BaseProvider):
    def __init__(self, provider_metadata: dict):
        super().__init__(provider_metadata)
        self.cache = {}
        
    def execute(self, eval_case: EvalCase) -> ProviderResult:
        cache_key = hashlib.md5(
            json.dumps(eval_case.dict()).encode()
        ).hexdigest()
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self._call_api(eval_case)
        self.cache[cache_key] = result
        return result
```

## Testing Your Provider

### Unit Tests

```python
# tests/test_custom_provider.py
from my_providers.custom_llm import CustomLLMProvider
from judge_llm.core.models import EvalCase

def test_custom_provider():
    provider = CustomLLMProvider({
        "agent_id": "test",
        "api_endpoint": "http://localhost:8000"
    })
    
    eval_case = create_test_eval_case()
    result = provider.execute(eval_case)
    
    assert result.success
    assert len(result.conversation_history) > 0
    assert result.cost >= 0.0
```

### Integration Tests

```python
from judge_llm import evaluate

def test_custom_provider_integration():
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["./test.json"]},
        providers=[{
            "type": "custom",
            "module_path": "./my_providers/custom_llm.py",
            "class_name": "CustomLLMProvider"
        }],
        evaluators=[{"type": "response_evaluator"}],
        reporters=[{"type": "console"}]
    )
    
    assert report.success_rate >= 0.8
```

## Troubleshooting

### Provider Not Found

**Error:** `Provider type 'my_custom' not found`

**Solution:** Register your provider:
```python
register_provider("my_custom", MyCustomProvider)
```

### Module Import Error

**Error:** `ModuleNotFoundError: No module named 'my_providers'`

**Solution:** Check `module_path` is correct relative to execution directory

### API Connection Failed

**Error:** `Connection refused`

**Solutions:**
- Check API endpoint URL
- Verify network connectivity
- Check firewall/proxy settings
- Test with curl first

## Related Documentation

- [Providers Overview](./overview.md)
- [Base Classes API](../api-reference/base-classes.md)
- [Configuration Guide](../guides/configuration.md)
- [Examples](../examples/custom-evaluator.md)
