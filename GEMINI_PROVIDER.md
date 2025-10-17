# Gemini Provider Implementation

## Overview

The Gemini provider has been successfully implemented following the BaseProvider signature and framework architecture.

## Implementation Details

### 1. Provider Class: [judge_llm/providers/gemini_provider.py](judge_llm/providers/gemini_provider.py)

**Key Features:**
- ✅ Inherits from `BaseProvider` with correct signature
- ✅ Uses `google-genai` SDK (`from google import genai`)
- ✅ Implements `__init__` with `agent_id`, `agent_config_path`, `agent_metadata`, and `**provider_metadata`
- ✅ Implements `execute(eval_case: EvalCase) -> ProviderResult`
- ✅ Implements `cleanup()` method
- ✅ API key from config or `GEMINI_API_KEY` environment variable
- ✅ Configurable model, temperature, max_tokens, top_p, top_k
- ✅ Automatic token usage tracking and cost calculation
- ✅ Proper error handling and logging
- ✅ Builds correct `Invocation` structure with `invocation_id`, `user_content`, `final_response`, `creation_timestamp`

**Constructor Signature:**
```python
def __init__(
    self,
    agent_id: str,
    agent_config_path: Optional[str] = None,
    agent_metadata: Optional[Dict[str, Any]] = None,
    **provider_metadata,
)
```

**Execute Signature:**
```python
def execute(self, eval_case: EvalCase) -> ProviderResult
```

### 2. Model Updates: [judge_llm/core/models.py](judge_llm/core/models.py)

**SessionInput Enhanced:**
```python
class SessionInput(BaseModel):
    app_name: str
    user_id: str
    state: Dict[str, Any] = Field(default_factory=dict)
    user_prompt: Optional[str] = None  # Added
    system_instruction: Optional[str] = None  # Added

    model_config = {"extra": "allow"}  # Allow additional fields
```

### 3. Auto-Registration: [judge_llm/providers/__init__.py](judge_llm/providers/__init__.py)

```python
# Optional providers (registered if dependencies are available)
try:
    from judge_llm.providers.gemini_provider import GeminiProvider
    register_provider("gemini", GeminiProvider)
except ImportError:
    pass  # google-genai not installed
```

### 4. Dependencies: [pyproject.toml](pyproject.toml)

```toml
[project.optional-dependencies]
gemini = [
    "google-genai>=0.1.0",
]
```

**Installation:**
```bash
pip install judge-llm[gemini]
```

## Configuration

### YAML Configuration Example

```yaml
agent:
  name: gemini_news_agent
  log_level: INFO
  num_runs: 1

dataset:
  loader: local_file
  paths:
    - ./sample.evalset.json

providers:
  - type: gemini
    agent_id: gemini_news_agent
    model: gemini-2.0-flash-exp
    temperature: 0.7
    max_tokens: 2048
    top_p: 0.95
    top_k: 40
    # API key from GEMINI_API_KEY environment variable

evaluators:
  - type: response_validator
    config:
      similarity_threshold: 0.7

  - type: latency_evaluator
    config:
      max_latency_seconds: 30

reporters:
  - type: console
  - type: json
    output_path: ./report.json
  - type: html
    output_path: ./report.html
```

### Programmatic Usage

```python
from judge_llm import evaluate
import os

# Set API key
os.environ["GEMINI_API_KEY"] = "your-api-key"

# Option 1: From config file
result = evaluate(config="config.yaml")

# Option 2: Programmatic
result = evaluate(
    agent={
        "name": "test_agent",
        "log_level": "INFO",
    },
    dataset={
        "loader": "local_file",
        "paths": ["./data.json"],
    },
    providers=[
        {
            "type": "gemini",
            "agent_id": "gemini_agent",
            "model": "gemini-2.0-flash-exp",
            "temperature": 0.7,
            "max_tokens": 2048,
        }
    ],
    evaluators=[
        {
            "type": "response_validator",
            "config": {"similarity_threshold": 0.7}
        }
    ],
    reporters=[
        {"type": "console"}
    ]
)

print(f"Success rate: {result.summary['success_rate']:.1%}")
print(f"Total cost: ${result.total_cost:.6f}")
```

## Validation Tests

### Test 1: Provider Registration
```bash
$ judge-llm list providers
Available Providers:
  - gemini
  - mock
```
✅ **PASSED**

### Test 2: Configuration Validation
```bash
$ cd examples/gemini
$ judge-llm validate --config config.yaml
✓ Configuration is valid
```
✅ **PASSED**

### Test 3: Provider Instantiation
```python
provider = GeminiProvider(
    agent_id='test_agent',
    model='gemini-2.0-flash-exp',
    temperature=0.7
)
```
✅ **PASSED**

### Test 4: Signature Compatibility
- ✅ `__init__` signature matches `BaseProvider`
- ✅ `execute` signature matches `BaseProvider`
- ✅ `cleanup` method implemented
- ✅ `get_provider_type()` returns "gemini"

### Test 5: Data Structure Compatibility
- ✅ Builds correct `Invocation` with all required fields
- ✅ Builds correct `ProviderResult` structure
- ✅ Handles `SessionInput` with user_prompt and system_instruction
- ✅ Extracts user prompt from eval case correctly

## Example Files

### Complete Example: [examples/gemini/](examples/gemini/)

**Files:**
- ✅ [config.yaml](examples/gemini/config.yaml) - Full configuration
- ✅ [sample.evalset.json](examples/gemini/sample.evalset.json) - 2 test cases
- ✅ [run_evaluation.py](examples/gemini/run_evaluation.py) - Python script
- ✅ [README.md](examples/gemini/README.md) - Comprehensive documentation

### Sample EvalSet Structure

```json
{
  "eval_set_id": "gemini_news_assistant_v1",
  "name": "News Assistant Evaluation - Gemini",
  "creation_timestamp": 1704067000.0,
  "eval_cases": [
    {
      "eval_id": "gemini_news_001",
      "conversation": [
        {
          "invocation_id": "test-001",
          "user_content": {
            "parts": [{"text": "What are the top technology news stories today?"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "Here are the top technology news stories..."}],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          },
          "creation_timestamp": 1704067200.0
        }
      ],
      "session_input": {
        "app_name": "news_assistant",
        "user_id": "test_user",
        "state": {},
        "user_prompt": "What are the top technology news stories today?",
        "system_instruction": "You are a helpful news assistant..."
      },
      "creation_timestamp": 1704067200.0
    }
  ]
}
```

## Available Gemini Models

| Model | Description | Use Case |
|-------|-------------|----------|
| `gemini-2.0-flash-exp` | Latest experimental flash model | Fast, cost-effective testing |
| `gemini-1.5-pro` | Most capable model | Complex reasoning tasks |
| `gemini-1.5-flash` | Balanced model | General-purpose usage |

## Cost Tracking

The provider automatically calculates costs based on token usage:

**Approximate Pricing (as of 2024):**
- Input tokens: $0.075 per 1M tokens
- Output tokens: $0.30 per 1M tokens

These rates are configurable in the provider code.

## Documentation Updates

### Updated Files:
- ✅ [README.md](README.md) - Added Providers section with Gemini details
- ✅ [.judge_llm.defaults.yaml](.judge_llm.defaults.yaml) - Added Gemini provider template
- ✅ [pyproject.toml](pyproject.toml) - Added google-genai dependency

## Usage Instructions

### Setup

1. **Install with Gemini support:**
   ```bash
   pip install -e ".[gemini]"
   ```

2. **Set API key:**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

   Get your API key from: https://makersuite.google.com/app/apikey

3. **Run evaluation:**
   ```bash
   cd examples/gemini
   judge-llm run --config config.yaml
   ```

### Environment Variable

The provider checks for API key in this order:
1. `api_key` in provider config (not recommended for production)
2. `GEMINI_API_KEY` environment variable (recommended)

## Error Handling

The provider handles errors gracefully:

```python
# Returns ProviderResult with success=False on error
result = ProviderResult(
    conversation_history=[],
    cost=0.0,
    time_taken=time_taken,
    token_usage={},
    metadata={
        "error": str(e),
        "provider": "gemini",
        ...
    },
    success=False
)
```

## Implementation Checklist

- ✅ Provider class inherits from BaseProvider
- ✅ Correct `__init__` signature with agent_id, agent_config_path, agent_metadata, **provider_metadata
- ✅ Correct `execute` signature taking only EvalCase
- ✅ Implements cleanup method
- ✅ Uses google-genai SDK
- ✅ API key from config or environment
- ✅ Builds correct Invocation structure
- ✅ Builds correct ProviderResult structure
- ✅ Token usage tracking
- ✅ Cost calculation
- ✅ Error handling and logging
- ✅ Auto-registration in providers/__init__.py
- ✅ Optional dependency in pyproject.toml
- ✅ Complete example with config and data
- ✅ Documentation in README.md
- ✅ Configuration validation passes
- ✅ Provider listed in `judge-llm list providers`

## Status: ✅ COMPLETE

The Gemini provider is fully implemented, tested, and documented according to the BaseProvider interface and framework architecture.
