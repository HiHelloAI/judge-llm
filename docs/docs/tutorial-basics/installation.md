---
sidebar_position: 1
---

# Installation

Install Judge LLM and set up your environment in under 2 minutes.

## Install via pip

```bash
pip install judge-llm
```

## Verify Installation

```bash
judge-llm --version
```

You should see the version number:
```
judge-llm version 0.1.0
```

## Set Up API Keys

Judge LLM supports multiple LLM providers. Set up the API keys for the providers you want to use.

### Method 1: Environment Variables (Recommended)

```bash
export GEMINI_API_KEY=your_gemini_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Method 2: .env File

Create a `.env` file in your project root:

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Judge LLM automatically loads `.env` files.

## Get API Keys

### Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy your API key

### Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Navigate to API Keys
3. Create a new key

## Test Your Setup

Create a simple test to verify everything works:

```bash
# Create a simple test file
cat > test.json << 'EOFJSON'
[
  {
    "eval_id": "test_001",
    "turns": [
      {"role": "user", "content": "What is 2+2?"},
      {"role": "assistant", "content": "4", "expected": true}
    ]
  }
]
EOFJSON

# Create config
cat > test.yaml << 'EOFYAML'
dataset:
  loader: local_file
  paths: [./test.json]
providers:
  - type: gemini
    agent_id: test
evaluators:
  - type: response_evaluator
reporters:
  - type: console
EOFYAML

# Run evaluation
judge-llm run --config test.yaml
```

If everything is set up correctly, you should see:

```
Starting evaluation...

Evaluation Progress:
  test_001: ✓ PASSED (cost: $0.0012, time: 1.2s)

Summary:
  Total Tests: 1
  Passed: 1
  Failed: 0
  Success Rate: 100.0%
```

## Next Steps

Now that you have Judge LLM installed, proceed to:

- [Your First Evaluation](./first-evaluation) - Run your first evaluation
- [Basic Usage Guide](../guides/basic-usage) - Learn common patterns
- [Examples](../examples) - Explore working examples

## Troubleshooting

### Command Not Found

**Error:** `judge-llm: command not found`

**Solution:**
```bash
# Ensure pip install location is in PATH
which judge-llm

# Or use Python module directly
python -m judge_llm.cli --version
```

### API Key Not Found

**Error:** `API key not found for provider: gemini`

**Solution:** Make sure you've set the environment variable or created `.env` file:
```bash
echo $GEMINI_API_KEY  # Should show your key
```

### Import Error

**Error:** `ModuleNotFoundError: No module named 'judge_llm'`

**Solution:**
```bash
# Reinstall
pip install --upgrade judge-llm

# Or install in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install judge-llm
```
