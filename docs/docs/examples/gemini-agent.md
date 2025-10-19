---
sidebar_position: 2
---

# Gemini Agent Evaluation

This example demonstrates the most basic usage of Judge LLM - evaluating a Gemini-powered agent with comprehensive evaluation capabilities.

## Overview

**Location:** `examples/01-gemini-agent/`

**Difficulty:** Beginner

**What You'll Learn:**
- Basic evaluation setup and configuration
- Configuring a Gemini provider
- Using multiple evaluators (response, trajectory, cost, latency)
- Running evaluations via CLI and Python API
- Multiple reporter outputs (console, JSON, HTML)

## Files

```
01-gemini-agent/
├── README.md              # Detailed instructions
├── config.yaml            # Configuration file
├── sample.evalset.json    # Test cases
├── run.sh                 # Shell script runner
└── run_evaluation.py      # Python API runner
```

## Prerequisites

### 1. Install Judge LLM

```bash
pip install judge-llm
```

### 2. Set Gemini API Key

Choose one method:

**Method 1: Environment Variable**
```bash
export GEMINI_API_KEY=your_api_key_here
```

**Method 2: .env File**
```bash
echo "GEMINI_API_KEY=your_key" > .env
```

**Method 3: Direct in Config** (not recommended)
```yaml
providers:
  - type: gemini
    api_key: "your_key"  # Not recommended for production
```

### 3. Get a Gemini API Key

Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your free API key.

## Configuration

### config.yaml

```yaml
# Gemini Provider Example Configuration
defaults: ../.judge_llm.defaults.yaml

agent:
  name: gemini_news_agent
  description: "News assistant using Google Gemini"
  log_level: INFO
  num_runs: 1
  parallel_execution: false
  max_workers: 1

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

evaluators:
  - type: response_evaluator
    enabled: true
    config:
      similarity_threshold: 0.7
      match_type: semantic
      case_sensitive: false

  - type: trajectory_evaluator
    enabled: true
    config:
      sequence_match_type: flexible
      allow_extra_steps: true

  - type: cost_evaluator
    enabled: true
    config:
      max_cost_per_case: 0.10
      currency: USD

  - type: latency_evaluator
    enabled: true
    config:
      max_latency_seconds: 30
      warn_threshold_seconds: 10

reporters:
  - type: console
  - type: json
    output_path: "../../reports/01-gemini-agent/gemini_report.json"
  - type: html
    output_path: "../../reports/01-gemini-agent/gemini_report.html"
```

### Configuration Breakdown

**Agent Settings:**
- `name`: Identifier for the agent being tested
- `description`: Human-readable description
- `log_level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `num_runs`: Number of times to run each test
- `parallel_execution`: Whether to run tests in parallel
- `max_workers`: Maximum parallel workers

**Gemini Provider:**
- `type: gemini`: Use Google's Gemini API
- `agent_id`: Links provider to agent
- `model`: Gemini model to use (flash-exp for latest experimental)
- `temperature`: Randomness (0.0 = deterministic, 1.0 = creative)
- `max_tokens`: Maximum response length
- `top_p`: Nucleus sampling parameter
- `top_k`: Top-k sampling parameter

**Evaluators:**

1. **Response Evaluator**: Checks if responses match expectations
   - `similarity_threshold`: Minimum similarity score (0.0-1.0)
   - `match_type`: How to compare (semantic, exact, regex)
   - `case_sensitive`: Whether to consider case

2. **Trajectory Evaluator**: Validates conversation flow
   - `sequence_match_type`: How strict (flexible, strict, ordered)
   - `allow_extra_steps`: Allow additional conversation turns

3. **Cost Evaluator**: Monitors API costs
   - `max_cost_per_case`: Maximum cost per test case
   - `currency`: Currency for reporting

4. **Latency Evaluator**: Tracks response times
   - `max_latency_seconds`: Maximum acceptable latency
   - `warn_threshold_seconds`: When to issue warnings

**Reporters:**
- `console`: Real-time output to terminal
- `json`: Structured data for programmatic access
- `html`: Visual report for human review

## Test Cases

### sample.evalset.json

```json
{
  "eval_set_id": "gemini_news_assistant_v1",
  "name": "News Assistant Evaluation - Gemini",
  "description": "Test cases for evaluating Gemini-powered news assistant",
  "eval_cases": [
    {
      "eval_id": "gemini_news_001",
      "conversation": [
        {
          "user_content": {
            "parts": [{"text": "What are the top technology news stories today?"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{
              "text": "Here are the top technology news stories:\n1. AI advances in healthcare diagnostics\n2. New quantum computing breakthrough announced\n3. Tech giants announce sustainability initiatives"
            }]
          }
        }
      ],
      "session_input": {
        "user_prompt": "What are the top technology news stories today?",
        "system_instruction": "You are a helpful news assistant that provides accurate, concise summaries of current events."
      }
    },
    {
      "eval_id": "gemini_news_002",
      "conversation": [
        {
          "user_content": {
            "parts": [{"text": "Can you explain what quantum computing is in simple terms?"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{
              "text": "Quantum computing is a new type of computing that uses quantum mechanics principles..."
            }]
          }
        }
      ],
      "session_input": {
        "user_prompt": "Can you explain what quantum computing is in simple terms?",
        "system_instruction": "You are a helpful news assistant. When explaining technical topics, use simple language."
      }
    }
  ]
}
```

### Test Case Structure

Each test case includes:

- `eval_id`: Unique identifier
- `conversation`: Array of turns with user/assistant messages
- `session_input`: Context including prompts and system instructions
- `final_response`: Expected response (used by evaluators)

## Running the Example

### Method 1: Command Line

```bash
cd examples/01-gemini-agent
judge-llm run --config config.yaml
```

### Method 2: Shell Script

```bash
cd examples/01-gemini-agent
chmod +x run.sh
./run.sh
```

### Method 3: Python API

```bash
cd examples/01-gemini-agent
python run_evaluation.py
```

## Expected Output

### Console Output

```
Starting evaluation...
Agent: gemini_news_agent
Description: News assistant using Google Gemini

Evaluation Progress:
  gemini_news_001: ✓ PASSED (cost: $0.0012, time: 1.2s)
    Response: ✓ PASSED (similarity: 0.85)
    Trajectory: ✓ PASSED
    Cost: ✓ PASSED ($0.0012 < $0.10)
    Latency: ✓ PASSED (1.2s < 30s)

  gemini_news_002: ✓ PASSED (cost: $0.0015, time: 1.5s)
    Response: ✓ PASSED (similarity: 0.92)
    Trajectory: ✓ PASSED
    Cost: ✓ PASSED ($0.0015 < $0.10)
    Latency: ✓ PASSED (1.5s < 30s)

Summary:
  Total Tests: 2
  Passed: 2
  Failed: 0
  Success Rate: 100.0%
  Total Cost: $0.0027
  Total Time: 2.7s
  Average Latency: 1.35s

Results saved to:
  - ../../reports/01-gemini-agent/gemini_report.json
  - ../../reports/01-gemini-agent/gemini_report.html
```

### JSON Output

```json
{
  "summary": {
    "total_tests": 2,
    "passed": 2,
    "failed": 0,
    "success_rate": 100.0,
    "total_cost": 0.0027,
    "total_time": 2.7,
    "average_latency": 1.35
  },
  "results": [
    {
      "eval_id": "gemini_news_001",
      "status": "passed",
      "evaluations": {
        "response": {"passed": true, "similarity": 0.85},
        "trajectory": {"passed": true},
        "cost": {"passed": true, "cost": 0.0012},
        "latency": {"passed": true, "latency": 1.2}
      }
    }
  ]
}
```

### HTML Report

Opens a visual report in your browser with:
- Summary statistics
- Pass/fail indicators
- Cost breakdown
- Latency graphs
- Detailed results per test

## Understanding Results

### Result Metrics

**Pass/Fail Status:**
- ✓ PASSED: All evaluators passed
- ✗ FAILED: One or more evaluators failed
- ⚠ WARNING: Passed but with warnings

**Response Evaluation:**
- Similarity score (0.0-1.0)
- Higher = better match with expected response
- Threshold configurable (default 0.7)

**Cost Tracking:**
- Cost per test case
- Total cost for all tests
- Compared against max_cost_per_case threshold

**Latency Tracking:**
- Time per test case
- Average latency
- Warnings if exceeds warn_threshold

**Trajectory:**
- Validates conversation flow
- Checks turn order and structure
- Can be strict or flexible

## Troubleshooting

### API Key Not Found

**Error:** `API key not found for provider: gemini`

**Solution:**
```bash
# Check if key is set
echo $GEMINI_API_KEY

# Set it if missing
export GEMINI_API_KEY=your_key

# Or use .env file
echo "GEMINI_API_KEY=your_key" > .env
```

### Test File Not Found

**Error:** `Test file not found: ./sample.evalset.json`

**Solution:**
```bash
# Ensure you're in the example directory
pwd
# Should output: .../examples/01-gemini-agent

# If not, navigate there
cd examples/01-gemini-agent
```

### Rate Limit Exceeded

**Error:** `Rate limit exceeded for Gemini API`

**Solution:**
- Wait and retry
- Reduce parallel execution
- Use a lower-tier model
- Check your quota at [Google Cloud Console](https://console.cloud.google.com/)

### Model Not Found

**Error:** `Model not found: gemini-2.0-flash-exp`

**Solution:**
```yaml
# Use stable model instead
providers:
  - type: gemini
    model: gemini-1.5-flash  # Stable version
```

## Customization

### Try Different Models

```yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp    # Latest experimental
    # OR
    model: gemini-1.5-flash         # Stable, fast
    # OR
    model: gemini-1.5-pro           # More capable
```

### Adjust Temperature

```yaml
providers:
  - type: gemini
    temperature: 0.0   # Deterministic, consistent
    # OR
    temperature: 0.7   # Balanced (default)
    # OR
    temperature: 1.0   # Creative, varied
```

### Add More Test Cases

Edit `sample.evalset.json`:

```json
{
  "eval_cases": [
    {
      "eval_id": "my_new_test",
      "conversation": [
        {
          "user_content": {
            "parts": [{"text": "Your question here"}]
          },
          "final_response": {
            "parts": [{"text": "Expected response"}]
          }
        }
      ]
    }
  ]
}
```

### Change Reporters

```yaml
reporters:
  # Console only (no files)
  - type: console

  # JSON for automation
  - type: json
    output_path: ./results.json

  # HTML for humans
  - type: html
    output_path: ./report.html

  # Database for tracking
  - type: database
    db_path: ./results.db
```

## Next Steps

After mastering this example:

1. **[Default Config](./default-config)** - Learn reusable configurations
2. **[Custom Evaluator](./custom-evaluator)** - Build domain-specific checks
3. **[Database Tracking](./database-tracking)** - Store and query results
4. **[Safety Evaluation](./safety-evaluation)** - Multi-turn conversations

## Related Documentation

- [Configuration Guide](../guides/configuration)
- [CLI Reference](../guides/cli-reference)
- [Python API](../guides/python-api)
- [Evalset Format](../guides/evalset-format)
- [Response Evaluator](../evaluators/response-evaluator)
- [Cost Evaluator](../evaluators/cost-evaluator)
- [Console Reporter](../reporters/console-reporter)
