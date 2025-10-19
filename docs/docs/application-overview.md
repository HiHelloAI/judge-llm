---
sidebar_position: 2
---

# Application Overview

A comprehensive guide to understanding Judge LLM's architecture, components, and design principles.

## What is Judge LLM?

Judge LLM is a lightweight, extensible Python framework designed to systematically evaluate and compare Large Language Model (LLM) providers. It provides a structured approach to testing AI agents, measuring performance, tracking costs, and ensuring quality before production deployment.

### Core Purpose

- **Systematic Testing**: Run repeatable, version-controlled test suites against your AI agents
- **Provider Comparison**: A/B test different LLM providers (Gemini, OpenAI, Anthropic, etc.)
- **Quality Assurance**: Validate response quality, latency, costs, and safety before deployment
- **Regression Prevention**: Catch performance degradations when models or code change
- **Cost Optimization**: Track and optimize API costs across different providers and models

## Architecture Overview

Judge LLM follows a modular, registry-based architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Judge LLM Framework                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Providers  │  │  Evaluators  │  │   Reporters  │         │
│  │              │  │              │  │              │         │
│  │ • Gemini     │  │ • Response   │  │ • Console    │         │
│  │ • OpenAI     │  │ • Trajectory │  │ • HTML       │         │
│  │ • Anthropic  │  │ • Cost       │  │ • JSON       │         │
│  │ • Mock       │  │ • Latency    │  │ • Database   │         │
│  │ • Custom     │  │ • Custom     │  │ • Custom     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│          │                 │                  │                 │
│          └─────────────────┼──────────────────┘                 │
│                            │                                    │
│                   ┌────────▼────────┐                          │
│                   │  Registry Core  │                          │
│                   │                 │                          │
│                   │ • Component     │                          │
│                   │   Registration  │                          │
│                   │ • Lifecycle     │                          │
│                   │   Management    │                          │
│                   │ • Configuration │                          │
│                   └────────┬────────┘                          │
│                            │                                    │
│              ┌─────────────┼─────────────┐                     │
│              │             │             │                     │
│     ┌────────▼──────┐  ┌──▼───────┐  ┌─▼──────────┐          │
│     │ Config Loader │  │ Evaluator│  │  Reporter  │          │
│     │               │  │ Engine   │  │  Engine    │          │
│     │ • YAML Parse  │  │          │  │            │          │
│     │ • Env Vars    │  │ • Execute│  │ • Format   │          │
│     │ • Merge       │  │ • Collect│  │ • Output   │          │
│     │ • Validate    │  │ • Report │  │ • Store    │          │
│     └───────────────┘  └──────────┘  └────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Providers

**Purpose:** Abstract away different LLM APIs into a unified interface.

**Built-in Providers:**
- **Gemini** - Google's Gemini API (Flash, Pro models)
- **Mock** - Testing provider that returns expected responses without API calls
- **Custom** - Extend for OpenAI, Anthropic, Azure, or any LLM API

**Key Responsibilities:**
- Send prompts to LLM APIs
- Handle authentication and rate limiting
- Track token usage and costs
- Return standardized response format
- Support conversation history/context

**Example:**
```python
from judge_llm.providers.base import BaseProvider

class MyProvider(BaseProvider):
    def invoke(self, messages, config):
        # Call your LLM API
        response = my_api.generate(messages)
        return {
            "content": response.text,
            "cost": response.usage.cost,
            "tokens": response.usage.tokens
        }
```

### 2. Evaluators

**Purpose:** Assess the quality and characteristics of LLM responses.

**Built-in Evaluators:**
- **Response Evaluator** - Semantic similarity, exact matching, ROUGE scores
- **Trajectory Evaluator** - Validates conversation flow and tool usage
- **Cost Evaluator** - Monitors API costs against budgets
- **Latency Evaluator** - Tracks response times and timeouts
- **Custom Evaluators** - Implement domain-specific validation

**Key Responsibilities:**
- Compare actual vs expected responses
- Calculate similarity/quality scores
- Validate conversation trajectories
- Monitor performance metrics
- Support per-test configuration overrides

**Example:**
```python
from judge_llm.evaluators.base import BaseEvaluator

class SafetyEvaluator(BaseEvaluator):
    def evaluate(self, test_case, response):
        is_safe = self.check_safety(response["content"])
        return EvaluationResult(
            evaluator_type="safety",
            passed=is_safe,
            score=1.0 if is_safe else 0.0,
            reason="Safe content" if is_safe else "Unsafe content detected"
        )
```

### 3. Reporters

**Purpose:** Format and output evaluation results for different use cases.

**Built-in Reporters:**
- **Console** - Real-time terminal output with colored formatting
- **HTML** - Interactive dashboard with charts and tables
- **JSON** - Structured data for programmatic access
- **Database** - SQLite storage for historical tracking and trends
- **Custom Reporters** - CSV, Slack notifications, custom dashboards

**Key Responsibilities:**
- Format evaluation results
- Generate visualizations
- Store historical data
- Enable trend analysis
- Support multiple output formats simultaneously

**Example:**
```python
from judge_llm.reporters.base import BaseReporter

class SlackReporter(BaseReporter):
    def report(self, evaluation_results):
        message = self.format_slack_message(results)
        self.slack_client.post_message(message)
```

### 4. Registry System

**Purpose:** Central component registration and lifecycle management.

**Features:**
- **Component Registration** - Register providers, evaluators, reporters by name
- **Lazy Loading** - Components instantiated only when needed
- **Configuration Binding** - Automatically inject configuration into components
- **Lifecycle Management** - Handle setup, execution, and cleanup
- **Type Safety** - Validate component types at registration

**Example:**
```python
from judge_llm.core.registry import Registry

# Register custom components
Registry.register_provider("my_provider", MyProvider)
Registry.register_evaluator("safety", SafetyEvaluator)

# Use by name in configuration
providers:
  - type: my_provider
evaluators:
  - type: safety
```

### 5. Configuration System

**Purpose:** Flexible, hierarchical configuration management.

**Configuration Sources (in precedence order):**
1. **Test Config** (`config.yaml`) - Specific test settings
2. **Project Defaults** (`.judge_llm.defaults.yaml`) - Project-wide defaults
3. **Global Defaults** (`~/.judge_llm/defaults.yaml`) - User defaults
4. **Built-in Defaults** - Framework defaults

**Key Features:**
- **Deep Merging** - Intelligently combine configurations
- **Environment Variables** - `${VAR_NAME:-default}` syntax
- **Validation** - Schema validation before execution
- **Per-Test Overrides** - Override evaluator settings per test case

**Example:**
```yaml
# .judge_llm.defaults.yaml (project defaults)
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.7

evaluators:
  - type: response_evaluator
  - type: cost_evaluator

# config.yaml (test-specific)
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - agent_id: my_agent  # Inherits type, model, temperature from defaults
```

## Data Flow

### Evaluation Execution Flow

```
1. Configuration Loading
   ├── Load test config (config.yaml)
   ├── Load project defaults (.judge_llm.defaults.yaml)
   ├── Load environment variables (.env)
   ├── Merge configurations (deep merge)
   └── Validate configuration schema

2. Component Initialization
   ├── Instantiate providers from registry
   ├── Instantiate evaluators from registry
   ├── Instantiate reporters from registry
   └── Inject configurations into components

3. Test Case Loading
   ├── Load evalset file(s)
   ├── Parse test cases
   ├── Validate test case format
   └── Apply per-test configuration overrides

4. Execution (for each test case)
   ├── Send prompt to provider
   ├── Receive response from LLM
   ├── Run all evaluators
   │   ├── Response Evaluator
   │   ├── Trajectory Evaluator
   │   ├── Cost Evaluator
   │   ├── Latency Evaluator
   │   └── Custom Evaluators
   └── Collect results

5. Reporting
   ├── Aggregate all test results
   ├── Calculate summary statistics
   ├── Format results per reporter
   │   ├── Console (real-time)
   │   ├── HTML (dashboard)
   │   ├── JSON (structured)
   │   └── Database (historical)
   └── Output to all reporters

6. Cleanup
   └── Close connections, clean up resources
```

### Test Case Structure

```json
{
  "eval_set_id": "test_suite_v1",
  "name": "Test Suite Name",
  "description": "Suite description",
  "eval_cases": [
    {
      "eval_id": "test_001",
      "conversation": [
        {
          "invocation_id": "inv_1",
          "user_content": {
            "parts": [{"text": "User prompt"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "Expected response"}]
          }
        }
      ],
      "session_input": {
        "user_prompt": "User prompt",
        "system_instruction": "System prompt"
      },
      "evaluator_config": {
        "ResponseEvaluator": {
          "similarity_threshold": 0.85
        }
      }
    }
  ]
}
```

## Design Principles

### 1. Extensibility First

Every core component (Provider, Evaluator, Reporter) can be extended:

```python
# Extend any base class
from judge_llm.providers.base import BaseProvider
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.reporters.base import BaseReporter

class MyComponent(Base*):
    def __init__(self, config):
        # Your initialization
        pass

    def method(self):
        # Your implementation
        pass
```

### 2. Configuration Over Code

Prefer declarative YAML configuration over imperative code:

```yaml
# config.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.8
```

### 3. Convention Over Configuration

Sensible defaults minimize required configuration:

```yaml
# Minimal config - uses built-in defaults
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini
    agent_id: my_agent
```

### 4. Composability

Mix and match components freely:

```yaml
providers:
  - type: gemini
  - type: openai
  - type: custom
    module_path: ./my_provider.py

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
  - type: custom
    module_path: ./my_evaluator.py

reporters:
  - type: console
  - type: html
  - type: database
```

### 5. Testability

Framework designed for easy testing:
- **Mock Provider** - Test without API calls
- **Isolated Components** - Unit test each component
- **Dependency Injection** - Easy to mock dependencies
- **Deterministic** - Consistent results with same inputs

## Use Cases

### 1. Regression Testing

**Scenario:** Ensure new model versions don't degrade quality

```yaml
# tests/regression_suite.yaml
dataset:
  loader: local_file
  paths: [./regression_tests.json]

providers:
  - type: gemini
    agent_id: production_agent
    model: ${MODEL_VERSION}

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.85

reporters:
  - type: database
    db_path: ./results.db
```

Run before/after model updates:
```bash
MODEL_VERSION=gemini-1.5-flash judge-llm run --config tests/regression_suite.yaml
MODEL_VERSION=gemini-2.0-flash judge-llm run --config tests/regression_suite.yaml
```

### 2. A/B Testing Providers

**Scenario:** Compare Gemini vs OpenAI vs Anthropic

```yaml
providers:
  - type: gemini
    agent_id: test_agent
    model: gemini-2.0-flash-exp

  - type: openai
    agent_id: test_agent
    model: gpt-4

  - type: anthropic
    agent_id: test_agent
    model: claude-3-sonnet

reporters:
  - type: html
    output_path: ./comparison.html
```

Framework automatically tests all providers and compares results.

### 3. Cost Optimization

**Scenario:** Find the cheapest model meeting quality requirements

```yaml
providers:
  - type: gemini
    model: gemini-1.5-flash    # Cheapest
  - type: gemini
    model: gemini-1.5-pro      # More capable
  - type: gemini
    model: gemini-2.0-flash    # Latest

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.8  # Minimum quality

  - type: cost_evaluator
    config:
      max_cost_per_case: 0.05

reporters:
  - type: database
```

Analyze results to find optimal price/performance ratio.

### 4. CI/CD Integration

**Scenario:** Automated testing in deployment pipeline

```yaml
# .github/workflows/test.yml
name: LLM Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Judge LLM
        run: pip install judge-llm
      - name: Run Tests
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: judge-llm run --config tests/ci_suite.yaml
      - name: Check Results
        run: |
          if [ $? -ne 0 ]; then
            echo "Tests failed!"
            exit 1
          fi
```

### 5. Safety Validation

**Scenario:** Validate responses don't contain harmful content

```python
# evaluators/safety_evaluator.py
from judge_llm.evaluators.base import BaseEvaluator

class SafetyEvaluator(BaseEvaluator):
    def evaluate(self, test_case, response):
        # Check for PII, toxicity, harmful instructions
        issues = []
        content = response["content"]

        if self.contains_pii(content):
            issues.append("PII detected")
        if self.is_toxic(content):
            issues.append("Toxic content")

        return EvaluationResult(
            passed=len(issues) == 0,
            reason="Safe" if not issues else f"Issues: {', '.join(issues)}"
        )
```

```yaml
# config.yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety_evaluator.py
    class_name: SafetyEvaluator
```

## Performance Considerations

### Parallel Execution

Run multiple test cases concurrently:

```yaml
agent:
  parallel_execution: true
  max_workers: 5
```

### Caching

Mock provider caches responses for development:

```yaml
providers:
  - type: mock
    cache_responses: true
```

### Database Optimization

Index frequently queried fields:

```sql
CREATE INDEX idx_eval_case_id ON execution_runs(eval_case_id);
CREATE INDEX idx_generated_at ON reports(generated_at);
```

## Best Practices

### 1. Start with Mock Provider

Develop test cases without API costs:

```yaml
providers:
  - type: mock
```

### 2. Use Default Configurations

Share common settings across tests:

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
```

### 3. Version Control Everything

```
project/
├── .judge_llm.defaults.yaml    # Project defaults
├── tests/
│   ├── regression_suite.yaml   # Test configs
│   ├── regression_tests.json   # Test cases
│   └── safety_tests.json
├── evaluators/                  # Custom evaluators
└── .env.example                # Environment template
```

### 4. Monitor Costs

Use database reporter to track spending:

```bash
sqlite3 results.db "
  SELECT
    DATE(generated_at) as date,
    SUM(total_cost) as daily_cost
  FROM reports
  GROUP BY DATE(generated_at)
  ORDER BY date DESC
"
```

### 5. Incremental Testing

Build up test suites gradually:
1. Start with basic happy path tests
2. Add edge cases
3. Add error scenarios
4. Add performance benchmarks
5. Add safety validations

## Next Steps

- **[Quick Start](./tutorial-basics/installation)** - Get started in 5 minutes
- **[Configuration Guide](./guides/configuration)** - Deep dive into configuration
- **[Examples](./examples/overview)** - Learn by example
- **[Custom Components](./evaluators/custom-evaluators)** - Extend the framework
- **[Python API](./guides/python-api)** - Programmatic usage
