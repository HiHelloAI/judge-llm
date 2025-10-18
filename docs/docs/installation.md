---
sidebar_position: 2
---

# Installation

Install Judge LLM and get started evaluating your LLM providers.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation Methods

### From Source (Recommended for Development)

```bash
git clone https://github.com/yourusername/judge-llm.git
cd judge-llm
pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install judge-llm
```

## Optional Dependencies

Install provider-specific dependencies based on your needs:

### Gemini Provider

```bash
pip install judge-llm[gemini]
```

Requires `GOOGLE_API_KEY` environment variable. Get your API key from: https://ai.google.dev/

### Development Dependencies

```bash
pip install judge-llm[dev]
```

Includes pytest, black, ruff for testing and development.

## Environment Setup

Judge LLM automatically loads environment variables from a `.env` file:

```bash
# Copy the example file
cp .env.example .env

# Edit and add your API keys
nano .env
```

Example `.env` file:

```bash
# Google Gemini API Key
GOOGLE_API_KEY=your-google-api-key-here
```

**Important**: Never commit `.env` to version control. It's already in `.gitignore`.

## Verify Installation

```bash
# Check CLI is available
judge-llm --version

# List available providers
judge-llm list providers

# List available evaluators
judge-llm list evaluators
```

## Next Steps

- [Quick Start Guide](./quick-start.md) - Run your first evaluation
- [Configuration Guide](./guides/configuration.md) - Learn about config files
- [Examples](./examples/overview.md) - Explore example projects
