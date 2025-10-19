---
sidebar_position: 6
---

# Examples

Learn by example with these comprehensive tutorials covering common Judge LLM use cases.

## Available Examples

### 1. Basic Gemini Agent Evaluation

**Location:** `examples/01-gemini-agent/`

Basic example demonstrating how to evaluate a Gemini agent with response evaluation.

**What you'll learn:**
- Setting up a basic evaluation
- Configuring Gemini provider
- Using response evaluator
- JSON output

**Files:**
- `test.yaml` - Configuration file
- `tests.json` - Test cases
- `README.md` - Detailed instructions

**Run:**
```bash
cd examples/01-gemini-agent
judge-llm run --config test.yaml
```

---

### 2. Default Configuration

**Location:** `examples/02-default-config/`

Demonstrates using `.judge_llm.defaults.yaml` to define reusable defaults.

**What you'll learn:**
- Creating default configuration
- Overriding defaults in test configs
- Configuration merging behavior
- DRY principle in practice

**Files:**
- `.judge_llm.defaults.yaml` - Default settings
- `test.yaml` - Test-specific config
- `tests.json` - Test cases
- `README.md` - Detailed instructions

**Run:**
```bash
cd examples/02-default-config
judge-llm run --config test.yaml
```

---

### 3. Custom Evaluator

**Location:** `examples/03-custom-evaluator/`

Build and use a custom evaluator to implement domain-specific validation.

**What you'll learn:**
- Creating custom evaluator classes
- Implementing BaseEvaluator interface
- Registering custom evaluators
- Combining built-in and custom evaluators

**Files:**
- `test.yaml` - Configuration with custom evaluator
- `tests.json` - Test cases
- `evaluators/safety_evaluator.py` - Custom evaluator implementation
- `README.md` - Detailed instructions

**Run:**
```bash
cd examples/03-custom-evaluator
judge-llm run --config test.yaml
```

---

### 4. Safety + Long Conversations

**Location:** `examples/04-safety-long-conversation/`

Evaluate multi-turn conversations with safety checks.

**What you'll learn:**
- Multi-turn conversation evaluation
- Safety evaluators
- Trajectory evaluation
- Handling long contexts

**Files:**
- `test.yaml` - Configuration
- `tests.json` - Multi-turn test cases
- `evaluators/safety_evaluator.py` - Safety checker
- `README.md` - Detailed instructions

**Run:**
```bash
cd examples/04-safety-long-conversation
judge-llm run --config test.yaml
```

---

### 5. Evaluator Config Override

**Location:** `examples/05-evaluator-config-override/`

Override evaluator configurations on a per-test basis.

**What you'll learn:**
- Overriding default evaluator settings
- Per-test configuration
- Cost and latency thresholds
- Multiple evaluator configurations

**Files:**
- `.judge_llm.defaults.yaml` - Default evaluator config
- `test.yaml` - Test with overrides
- `tests.json` - Test cases
- `README.md` - Detailed instructions

**Run:**
```bash
cd examples/05-evaluator-config-override
judge-llm run --config test.yaml
```

---

### 6. Database Reporter

**Location:** `examples/06-database-reporter/`

Store evaluation results in SQLite for historical tracking and analysis.

**What you'll learn:**
- Using database reporter
- Querying historical results
- Trend analysis
- Dashboard generation

**Files:**
- `test.yaml` - Configuration with database reporter
- `tests.json` - Test cases
- `query_results.py` - Sample SQL queries
- `README.md` - Detailed instructions

**Run:**
```bash
cd examples/06-database-reporter
judge-llm run --config test.yaml

# Query results
python query_results.py
```

---

### 7. Custom Reporter (CSV)

**Location:** `examples/custom_reporter_example/`

Implement a custom CSV reporter for exporting results.

**What you'll learn:**
- Creating custom reporter classes
- Implementing BaseReporter interface
- Registering custom reporters
- File-based output

**Files:**
- `test.yaml` - Configuration with custom reporter
- `tests.json` - Test cases
- `reporters/csv_reporter.py` - Custom reporter implementation
- `README.md` - Detailed instructions

**Run:**
```bash
cd examples/custom_reporter_example
judge-llm run --config test.yaml
```

---

### 8. Default Config Registration

**Location:** `examples/default_config_reporters/`

Register custom components in default config for reuse across all tests.

**What you'll learn:**
- Registering custom providers in defaults
- Registering custom evaluators in defaults
- Registering custom reporters in defaults
- Using `register_as` field
- Component reusability

**Files:**
- `.judge_llm.defaults.yaml` - Component registrations
- `test.yaml` - Test using registered components
- `tests.json` - Test cases
- `providers/my_provider.py` - Custom provider
- `evaluators/safety.py` - Custom evaluator
- `reporters/csv_reporter.py` - Custom reporter
- `README.md` - Detailed instructions

**Run:**
```bash
cd examples/default_config_reporters
judge-llm run --config test.yaml
```

---

## Running All Examples

To test all examples at once:

```bash
#!/bin/bash

EXAMPLES=(
    "01-gemini-agent"
    "02-default-config"
    "03-custom-evaluator"
    "04-safety-long-conversation"
    "05-evaluator-config-override"
    "06-database-reporter"
    "custom_reporter_example"
    "default_config_reporters"
)

for example in "${EXAMPLES[@]}"; do
    echo "================================================"
    echo "Running example: $example"
    echo "================================================"
    cd "examples/$example"
    judge-llm run --config test.yaml
    cd ../..
done
```

## Example Categories

### By Difficulty

**Beginner:**
1. Basic Gemini Agent Evaluation
2. Default Configuration

**Intermediate:**
3. Custom Evaluator
4. Evaluator Config Override
5. Database Reporter
6. Custom Reporter

**Advanced:**
7. Safety + Long Conversations
8. Default Config Registration

### By Feature

**Configuration:**
- Default Configuration (02)
- Evaluator Config Override (05)
- Default Config Registration (08)

**Custom Components:**
- Custom Evaluator (03)
- Custom Reporter (07)
- Default Config Registration (08)

**Reporters:**
- Database Reporter (06)
- Custom Reporter (07)

**Evaluators:**
- Custom Evaluator (03)
- Safety + Long Conversations (04)
- Evaluator Config Override (05)

**Multi-turn:**
- Safety + Long Conversations (04)

## Quick Reference

| Example | Focus | Difficulty | Key Concepts |
|---------|-------|------------|--------------|
| 01 | Basic setup | Beginner | Configuration, providers, evaluators |
| 02 | Defaults | Beginner | Default config, config merging |
| 03 | Custom evaluator | Intermediate | Custom components, registration |
| 04 | Multi-turn | Advanced | Long conversations, safety, trajectory |
| 05 | Config override | Intermediate | Per-test config, thresholds |
| 06 | Database | Intermediate | SQLite, querying, trends |
| 07 | Custom reporter | Intermediate | Custom output, file handling |
| 08 | Registration | Advanced | Reusable components, DRY |

## Common Patterns

### Setting Up Environment

All examples assume you have:

1. **Installed Judge LLM:**
```bash
pip install judge-llm
```

2. **Set API keys in `.env`:**
```bash
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

3. **Navigate to example directory:**
```bash
cd examples/XX-example-name
```

### Reading Examples

Each example includes:

1. **README.md** - Detailed explanation and instructions
2. **test.yaml** - Configuration file
3. **tests.json** - Test cases
4. **Additional files** - Custom implementations (evaluators, reporters, providers)

### Modifying Examples

To experiment with an example:

1. Copy the example directory
2. Modify configuration or code
3. Run with your changes
4. Compare results

**Example:**
```bash
cp -r examples/01-gemini-agent my-test
cd my-test
# Edit test.yaml or tests.json
judge-llm run --config test.yaml
```

## Example Output

When running examples, you'll see output like:

```
Starting evaluation...

Evaluation Progress:
  test_001: ✓ PASSED (cost: $0.0012, time: 1.2s)
  test_002: ✓ PASSED (cost: $0.0015, time: 1.5s)
  test_003: ✗ FAILED (cost: $0.0010, time: 0.8s)

Summary:
  Total Tests: 3
  Passed: 2
  Failed: 1
  Success Rate: 66.7%
  Total Cost: $0.0037
  Total Time: 3.5s

Results saved to ./results.json
```

## Troubleshooting Examples

### API Key Not Set

**Error:** `API key not found for provider: gemini`

**Solution:** Create `.env` file with your API key:
```bash
echo "GEMINI_API_KEY=your_key" > .env
```

### Module Not Found

**Error:** `Module not found: ./evaluators/safety.py`

**Solution:** Ensure you're in the example directory:
```bash
pwd
# Should be: /path/to/judge_llm/examples/XX-example-name
```

### Tests Not Found

**Error:** `Test file not found: ./tests.json`

**Solution:** Check test file exists:
```bash
ls tests.json
```

## Contributing Examples

Want to add your own example? Follow these steps:

1. **Create directory:**
```bash
mkdir examples/XX-your-example
cd examples/XX-your-example
```

2. **Add required files:**
- `README.md` - Description and instructions
- `test.yaml` - Configuration
- `tests.json` - Test cases
- Additional implementations as needed

3. **Document:**
- Explain what the example demonstrates
- List key concepts
- Provide step-by-step instructions
- Include expected output

4. **Test:**
```bash
judge-llm run --config test.yaml
```

5. **Submit PR:**
Include example in documentation update.

## Related Documentation

- [Quick Start](./tutorial-basics/installation)
- [Configuration Guide](./guides/configuration)
- [CLI Reference](./guides/cli-reference)
- [Python API](./guides/python-api)
- [Custom Evaluators](./evaluators/custom-evaluators)
- [Custom Reporters](./reporters/custom-reporters)
