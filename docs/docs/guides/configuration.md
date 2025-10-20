---
sidebar_position: 3
---

# Configuration Guide

Comprehensive guide to configuring Judge LLM evaluations using YAML files.

## Configuration File Structure

Judge LLM uses YAML configuration files to define evaluations. The basic structure includes four main sections:

```yaml
dataset:
  # Data loading configuration

providers:
  # LLM provider(s) to evaluate

evaluators:
  # Evaluation criteria

reporters:
  # Output format(s)
```

## Dataset Configuration

The `dataset` section specifies where to load test cases from.

### Local File Loader

Load test cases from JSON files on your local filesystem.

```yaml
dataset:
  loader: local_file
  paths:
    - ./tests.json
    - ./more_tests.json
```

**Test File Format:**

```json
[
  {
    "eval_id": "test_001",
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
  }
]
```

### BrowserBase Loader

Load test cases from BrowserBase sessions (for web-based testing).

```yaml
dataset:
  loader: browserbase
  api_key: ${BROWSERBASE_API_KEY}
  project_id: ${BROWSERBASE_PROJECT_ID}
```

## Provider Configuration

The `providers` section defines which LLM(s) to evaluate. You can configure single or multiple providers to test and compare different models.

### Gemini Provider

Google's Gemini models via the official API.

```yaml
providers:
  - type: gemini
    agent_id: gemini_agent
    model: gemini-2.0-flash-exp
    temperature: 0.0
    max_tokens: 8192
    top_p: 0.95
    top_k: 40
    api_key: ${GOOGLE_API_KEY}
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Provider type (`gemini`) | - | Yes |
| `agent_id` | Unique identifier for this agent | - | Yes |
| `model` | Model name | `gemini-2.0-flash-exp` | No |
| `temperature` | Sampling temperature (0-1) | `1.0` | No |
| `max_tokens` | Maximum response tokens | `8192` | No |
| `top_p` | Top-p sampling (0-1) | `0.95` | No |
| `top_k` | Top-k sampling | `40` | No |
| `api_key` | API key | `${GOOGLE_API_KEY}` | No |

**Supported Models:**
- `gemini-2.0-flash-exp` - Latest experimental flash model (recommended)
- `gemini-1.5-flash` - Fast, cost-effective model
- `gemini-1.5-pro` - High capability model
- `gemini-1.5-flash-8b` - Ultra-fast, lightweight model

**Note:** Requires `GOOGLE_API_KEY` environment variable or explicit `api_key` parameter.

### Mock Provider

Built-in test provider that returns expected responses without API calls. Perfect for testing and development.

```yaml
providers:
  - type: mock
    agent_id: test_agent
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Provider type (`mock`) | - | Yes |
| `agent_id` | Unique identifier | - | Yes |

**Features:**
- No API calls - returns conversation history from test cases
- Instant execution - no network latency
- Cost calculation - mock token counting for testing
- No authentication required

**Use Cases:**
- Development and testing
- CI/CD without API costs
- Validating test case structure
- Framework development

### Google ADK Provider

Google's Agent Development Kit for building AI agents with tool use.

```yaml
providers:
  - type: google_adk
    agent_id: adk_agent
    agent_metadata:
      module_path: "my_agent.agent"
      agent_name: "root_agent"
      root_path: "."
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Provider type (`google_adk`) | - | Yes |
| `agent_id` | Unique identifier | - | Yes |
| `agent_metadata.module_path` | Python module path to agent | - | Yes |
| `agent_metadata.agent_name` | Agent variable name in module | `root_agent` | No |
| `agent_metadata.root_path` | Root directory for imports | `.` | No |

**Features:**
- Async agent execution
- Tool calling support
- Multi-turn conversations
- Session management
- Thread-safe agent caching

See the `examples/09-google-adk-agent` directory in the repository for a complete setup guide.

### OpenAI Provider

OpenAI's GPT models (requires custom implementation).

```yaml
providers:
  - type: openai
    agent_id: openai_agent
    model: gpt-4
    temperature: 0.7
    max_tokens: 2048
    api_key: ${OPENAI_API_KEY}
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Provider type (`openai`) | - | Yes |
| `agent_id` | Unique identifier | - | Yes |
| `model` | Model name | `gpt-4` | No |
| `temperature` | Sampling temperature (0-1) | `0.7` | No |
| `max_tokens` | Maximum response tokens | `2048` | No |
| `api_key` | API key | `${OPENAI_API_KEY}` | No |

**Note:** Requires custom provider implementation. See [Custom Providers](#custom-providers) below.

### Anthropic Provider

Anthropic's Claude models (requires custom implementation).

```yaml
providers:
  - type: anthropic
    agent_id: claude_agent
    model: claude-3-5-sonnet-20241022
    temperature: 0.0
    max_tokens: 4096
    api_key: ${ANTHROPIC_API_KEY}
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Provider type (`anthropic`) | - | Yes |
| `agent_id` | Unique identifier | - | Yes |
| `model` | Model name | `claude-3-5-sonnet-20241022` | No |
| `temperature` | Sampling temperature (0-1) | `1.0` | No |
| `max_tokens` | Maximum response tokens | `4096` | No |
| `api_key` | API key | `${ANTHROPIC_API_KEY}` | No |

**Note:** Requires custom provider implementation. See [Custom Providers](#custom-providers) below.

### Multiple Providers (A/B Testing)

Compare multiple models in a single evaluation run. Each provider evaluates the same test cases independently.

```yaml
providers:
  - type: gemini
    agent_id: gemini_flash
    model: gemini-2.0-flash-exp
    temperature: 0.0

  - type: gemini
    agent_id: gemini_pro
    model: gemini-1.5-pro
    temperature: 0.0

  - type: mock
    agent_id: baseline
```

**Benefits:**
- Compare response quality across models
- Compare cost and latency
- Identify best model for your use case
- Regression testing when switching models

**Output:** Each provider generates separate execution runs in the report, allowing side-by-side comparison.

### Custom Providers

Implement custom providers for any LLM API or service.

```yaml
providers:
  - type: custom
    module_path: ./providers/my_provider.py
    class_name: MyCustomProvider
    agent_id: custom_agent
    # Custom config options passed to provider
    endpoint: https://api.example.com
    api_key: ${CUSTOM_API_KEY}
    timeout: 30
```

**Implementation Example:**

```python
# providers/my_provider.py
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult, Invocation, Content, Part

class MyCustomProvider(BaseProvider):
    def __init__(self, agent_id, agent_config_path=None, agent_metadata=None, **provider_metadata):
        super().__init__(agent_id, agent_config_path, agent_metadata, **provider_metadata)

        # Access custom config
        self.endpoint = provider_metadata.get("endpoint")
        self.api_key = provider_metadata.get("api_key")
        self.timeout = provider_metadata.get("timeout", 30)

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """Execute evaluation case using your custom LLM."""
        try:
            # Call your LLM API
            response = self._call_llm_api(eval_case)

            # Build conversation history
            conversation_history = [
                Invocation(
                    invocation_id=inv.invocation_id,
                    user_content=inv.user_content,
                    final_response=Content(
                        parts=[Part(text=response["text"])],
                        role="model"
                    ),
                    intermediate_data=inv.intermediate_data,
                    creation_timestamp=inv.creation_timestamp
                )
                for inv in eval_case.conversation
            ]

            return ProviderResult(
                conversation_history=conversation_history,
                cost=response.get("cost", 0.0),
                token_usage=response.get("tokens", {}),
                metadata={
                    "provider": "custom",
                    "agent_id": self.agent_id,
                    "model": response.get("model")
                },
                success=True
            )

        except Exception as e:
            return ProviderResult(
                conversation_history=[],
                success=False,
                error=str(e)
            )

    def _call_llm_api(self, eval_case):
        """Call your custom LLM API."""
        # Your implementation here
        pass

    def cleanup(self):
        """Cleanup resources."""
        pass
```

**Registration Options:**

1. **Inline in config** (shown above)
2. **Register globally** in `.judge_llm.defaults.yaml`:

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: custom
    module_path: ./providers/my_provider.py
    class_name: MyCustomProvider
    register_as: my_provider  # ← Register globally

# Then use by name in test configs
providers:
  - type: my_provider  # ← Uses registered provider
    agent_id: test_agent
```

See [Custom Component Registration](#custom-component-registration) for more details.

## Agent Configuration

The `agent` section controls execution behavior and quality gates.

```yaml
agent:
  num_runs: 1                           # Number of times to run each test case
  parallel_execution: false             # Run tests in parallel
  max_workers: 4                        # Max parallel workers (if parallel enabled)
  fail_on_threshold_violation: true    # Exit with error if evaluations fail
  log_level: INFO                       # Logging level (DEBUG|INFO|WARNING|ERROR)
```

### Configuration Options

| Option | Description | Default | Type |
|--------|-------------|---------|------|
| `num_runs` | Number of times to execute each eval case | `1` | integer |
| `parallel_execution` | Enable parallel execution of test cases | `false` | boolean |
| `max_workers` | Maximum number of parallel worker threads | `4` | integer |
| `fail_on_threshold_violation` | Exit with error code when evaluator thresholds are violated | `true` | boolean |
| `log_level` | Logging verbosity level | `INFO` | string |

### fail_on_threshold_violation

**Purpose:** Controls whether the evaluation process should fail (exit with error code 1) when any evaluator thresholds are violated.

**Use Cases:**

**✅ When to enable (`fail_on_threshold_violation: true`):**
- **CI/CD Pipelines**: Fail builds when LLM quality drops below thresholds
- **Regression Testing**: Prevent deployments if model performance degrades
- **Quality Gates**: Enforce minimum quality standards before production
- **Pre-commit Hooks**: Block commits that violate quality thresholds

```yaml
# CI/CD configuration - fail on violations
agent:
  fail_on_threshold_violation: true  # Block deployments if quality drops

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.85  # Minimum 85% similarity required
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.05     # Maximum $0.05 per test
```

**📊 When to disable (`fail_on_threshold_violation: false`):**
- **Monitoring & Reporting**: Track metrics over time without failing
- **Exploratory Testing**: Test new models/prompts without strict requirements
- **Development**: Iterate quickly without strict quality gates
- **Gradual Rollout**: Collect data before enforcing thresholds

```yaml
# Monitoring configuration - collect data without failing
agent:
  fail_on_threshold_violation: false  # Continue despite violations

reporters:
  - type: database
    db_path: ./metrics.db  # Track trends over time
```

**Error Output Example:**

When violations occur with `fail_on_threshold_violation: true`, you'll see:

```
================================================================================
  THRESHOLD VIOLATION DETECTED
================================================================================

❌ 3/10 evaluation(s) failed to meet thresholds
Success rate: 70.0% (100% required)

Failed evaluation cases:
  • test_001 (run 1) - Failed: response, cost
  • test_003 (run 1) - Failed: latency
  • test_007 (run 1) - Failed: trajectory

================================================================================
💡 TIP: Set 'fail_on_threshold_violation: false' in agent config to continue
        despite threshold violations (useful for monitoring/testing)
================================================================================
```

Exit code: `1` (failure)

### Parallel Execution

Enable parallel execution to speed up large test suites:

```yaml
agent:
  parallel_execution: true
  max_workers: 8  # Use 8 parallel threads
  num_runs: 3     # Each test runs 3 times in parallel
```

**Performance Tips:**
- Set `max_workers` based on your CPU cores (typically 2x cores)
- Parallel execution reduces wall-clock time but not total execution time
- Monitor memory usage with large test suites

## Evaluator Configuration

The `evaluators` section defines how responses are evaluated.

### Response Evaluator

Evaluates response correctness using an LLM judge.

```yaml
evaluators:
  - type: response_evaluator
    llm_provider: gemini
    llm_model: gemini-2.0-flash-exp
    temperature: 0.0
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Evaluator type | - | Yes |
| `llm_provider` | LLM for judging | `gemini` | No |
| `llm_model` | Model for judging | Provider default | No |
| `temperature` | Temperature for judge | `0.0` | No |

### Trajectory Evaluator

Evaluates the reasoning process and intermediate steps.

```yaml
evaluators:
  - type: trajectory_evaluator
    llm_provider: gemini
    llm_model: gemini-2.0-flash-exp
```

### Cost Evaluator

Ensures cost stays within threshold.

```yaml
evaluators:
  - type: cost_evaluator
    max_cost: 0.01  # Fail if cost > $0.01
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Evaluator type | - | Yes |
| `max_cost` | Maximum cost threshold | - | Yes |

### Latency Evaluator

Ensures response time stays within threshold.

```yaml
evaluators:
  - type: latency_evaluator
    max_latency: 5.0  # Fail if latency > 5 seconds
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Evaluator type | - | Yes |
| `max_latency` | Maximum latency (seconds) | - | Yes |

### Multiple Evaluators

Combine multiple evaluation criteria:

```yaml
evaluators:
  - type: response_evaluator
    llm_provider: gemini
    
  - type: trajectory_evaluator
    llm_provider: gemini
    
  - type: cost_evaluator
    max_cost: 0.01
    
  - type: latency_evaluator
    max_latency: 3.0
```

All evaluators must pass for a test case to be considered successful.

### Custom Evaluators

```yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
    # Custom config options
    strict_mode: true
```

## Reporter Configuration

The `reporters` section defines how results are output.

### Console Reporter

Print results to terminal.

```yaml
reporters:
  - type: console
```

No additional configuration required.

### JSON Reporter

Export results as JSON.

```yaml
reporters:
  - type: json
    output_path: ./results.json
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Reporter type | - | Yes |
| `output_path` | Path to JSON file | - | Yes |

### HTML Reporter

Generate interactive HTML report.

```yaml
reporters:
  - type: html
    output_path: ./report.html
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Reporter type | - | Yes |
| `output_path` | Path to HTML file | - | Yes |

### Database Reporter

Store results in SQLite database.

```yaml
reporters:
  - type: database
    db_path: ./results.db
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `type` | Reporter type | - | Yes |
| `db_path` | Path to SQLite database | - | Yes |

### Multiple Reporters

Use multiple output formats simultaneously:

```yaml
reporters:
  - type: console
  
  - type: json
    output_path: ./results.json
    
  - type: html
    output_path: ./report.html
    
  - type: database
    db_path: ./results.db
```

### Custom Reporters

```yaml
reporters:
  - type: custom
    module_path: ./reporters/slack.py
    class_name: SlackReporter
    webhook_url: ${SLACK_WEBHOOK_URL}
    channel: "#evals"
```

## Environment Variables

Use environment variables for sensitive data and configuration that changes between environments.

### Syntax

Reference environment variables using `${VAR_NAME}` syntax:

```yaml
providers:
  - type: gemini
    agent_id: ${AGENT_ID}
    api_key: ${GEMINI_API_KEY}
    model: ${MODEL:-gemini-2.0-flash-exp}  # Default value
```

### Loading from .env

Create a `.env` file in your project root:

```bash
# .env
AGENT_ID=my_agent
GEMINI_API_KEY=your_api_key
OPENAI_API_KEY=your_openai_key
MODEL=gemini-2.0-flash-exp
```

Judge LLM automatically loads `.env` files when running evaluations.

### Environment-Specific Configuration

```yaml
# dev.yaml
providers:
  - type: gemini
    agent_id: dev_agent
    model: ${DEV_MODEL}
    api_key: ${DEV_API_KEY}

# prod.yaml
providers:
  - type: gemini
    agent_id: prod_agent
    model: ${PROD_MODEL}
    api_key: ${PROD_API_KEY}
```

## Default Configuration

Create a `.judge_llm.defaults.yaml` file to define reusable defaults.

### Project Defaults

Place in project root: `.judge_llm.defaults.yaml`

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

evaluators:
  - type: response_evaluator
    llm_provider: gemini
  
  - type: cost_evaluator
    max_cost: 0.05

reporters:
  - type: console
  
  - type: json
    output_path: ./results/latest.json
```

### Global Defaults

Place in home directory: `~/.judge_llm/defaults.yaml`

```yaml
# ~/.judge_llm/defaults.yaml
providers:
  - type: gemini
    api_key: ${GEMINI_API_KEY}
    temperature: 0.0

reporters:
  - type: console
```

### Merging Behavior

Defaults are merged with your test config:

1. Global defaults (`~/.judge_llm/defaults.yaml`)
2. Project defaults (`.judge_llm.defaults.yaml`)
3. Test config (`test.yaml`)

Test config values override defaults.

## Custom Component Registration

Register custom components in default config for reuse across multiple test configs.

### Registering Providers

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: custom
    module_path: ./providers/my_provider.py
    class_name: MyProvider
    register_as: my_provider  # ← Register globally
```

Use by name in test configs:

```yaml
# test.yaml
providers:
  - type: my_provider  # ← Use by name
    agent_id: test_agent
```

### Registering Evaluators

```yaml
# .judge_llm.defaults.yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
    register_as: safety
```

Use by name:

```yaml
# test.yaml
evaluators:
  - type: safety
  - type: response_evaluator
```

### Registering Reporters

```yaml
# .judge_llm.defaults.yaml
reporters:
  - type: custom
    module_path: ./reporters/csv.py
    class_name: CSVReporter
    register_as: csv
```

Use by name:

```yaml
# test.yaml
reporters:
  - type: csv
    output_path: ./results.csv
```

## Complete Configuration Examples

### Basic Single-Provider Test

```yaml
dataset:
  loader: local_file
  paths:
    - ./tests.json

providers:
  - type: gemini
    agent_id: test_agent

evaluators:
  - type: response_evaluator

reporters:
  - type: console
```

### Multi-Provider A/B Test

```yaml
dataset:
  loader: local_file
  paths:
    - ./tests.json

providers:
  - type: gemini
    agent_id: gemini
    model: gemini-2.0-flash-exp
    
  - type: openai
    agent_id: openai
    model: gpt-4

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.01
  - type: latency_evaluator
    max_latency: 5.0

reporters:
  - type: console
  - type: html
    output_path: ./comparison.html
  - type: database
    db_path: ./ab_test.db
```

### Production Configuration

```yaml
dataset:
  loader: local_file
  paths:
    - ./tests/smoke.json
    - ./tests/regression.json

providers:
  - type: gemini
    agent_id: prod_agent
    model: ${PROD_MODEL}
    temperature: 0.0
    api_key: ${GEMINI_API_KEY}

evaluators:
  - type: response_evaluator
    llm_provider: gemini
    
  - type: trajectory_evaluator
    llm_provider: gemini
    
  - type: cost_evaluator
    max_cost: 0.05
    
  - type: latency_evaluator
    max_latency: 3.0

reporters:
  - type: console
  
  - type: json
    output_path: ./results/prod-${date}.json
    
  - type: html
    output_path: ./reports/prod-${date}.html
    
  - type: database
    db_path: ./results.db
```

## Configuration Validation

Validate your configuration before running:

```bash
judge-llm validate --config test.yaml
```

Common validation errors:

| Error | Solution |
|-------|----------|
| Missing required field | Add the required field to your config |
| Invalid provider type | Check provider type name (gemini, openai, anthropic) |
| Invalid evaluator type | Check evaluator type name |
| Invalid reporter type | Check reporter type name |
| Invalid file path | Ensure paths are correct and accessible |
| Missing API key | Set environment variable or add to .env |

## Best Practices

### 1. Use Environment Variables for Secrets

**Bad:**
```yaml
providers:
  - type: gemini
    api_key: "AIzaSyA..."  # Hard-coded secret
```

**Good:**
```yaml
providers:
  - type: gemini
    api_key: ${GEMINI_API_KEY}
```

### 2. Organize Configs by Environment

```
configs/
  ├── dev.yaml
  ├── staging.yaml
  └── prod.yaml
```

### 3. Use Defaults for Common Settings

Put common settings in `.judge_llm.defaults.yaml`:

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: gemini
    temperature: 0.0
    model: gemini-2.0-flash-exp

evaluators:
  - type: cost_evaluator
    max_cost: 0.05
```

Keep test configs focused:

```yaml
# test.yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - agent_id: my_test  # Other settings from defaults
```

### 4. Version Control Configuration

Include in git:
- Configuration files (`.yaml`)
- Default configuration (`.judge_llm.defaults.yaml`)

Exclude from git (`.gitignore`):
- `.env` (contains secrets)
- Results files (`*.json`, `*.html`, `*.db`)

### 5. Document Custom Configuration

Add comments to explain custom settings:

```yaml
providers:
  - type: gemini
    agent_id: specialized_agent
    temperature: 0.8  # Higher temperature for creative tasks
    max_tokens: 4096  # Longer responses needed
```

## Troubleshooting

### Configuration Not Found

**Error:** `Configuration file not found`

**Solution:** Check file path and ensure it exists:
```bash
ls -la test.yaml
```

### Environment Variable Not Set

**Error:** `API key not found for provider: gemini`

**Solution:** Set the environment variable:
```bash
export GEMINI_API_KEY=your_key
# Or add to .env file
```

### Invalid YAML Syntax

**Error:** `YAML parsing error`

**Solution:** Validate YAML syntax:
```bash
# Use yamllint or online YAML validator
yamllint test.yaml
```

### Custom Component Not Found

**Error:** `Module not found: ./providers/my_provider.py`

**Solution:** Check module path is correct relative to config file location.

## Related Documentation

- [CLI Reference](./cli-reference)
- [Python API Reference](./python-api)
- [Quick Start](../tutorial-basics/installation)
- [Custom Evaluators](../evaluators/custom-evaluators)
- [Custom Reporters](../reporters/custom-reporters)
