# Contributing to Judge LLM

Thank you for your interest in contributing to Judge LLM! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [License](#license)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and considerate in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Personal attacks or insults
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git for version control
- Basic understanding of LLM evaluation concepts

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/judge-llm.git
   cd judge-llm
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/HiHelloAI/judge-llm.git
   ```

## Development Setup

### 1. Create a Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n judge-llm python=3.9
conda activate judge-llm
```

### 2. Install Development Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install optional provider dependencies if needed
pip install -e ".[gemini]"
pip install -e ".[google_adk]"
```

### 3. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys (if testing providers)
nano .env
```

### 4. Verify Installation

```bash
# Run tests to verify setup
pytest

# Check code formatting
black judge_llm --check
ruff check judge_llm
```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

#### 1. Bug Fixes
- Fix bugs reported in issues
- Add tests to prevent regression
- Update documentation if behavior changes

#### 2. New Features
- Add new providers (OpenAI, Anthropic, etc.)
- Create new evaluators (safety, compliance, etc.)
- Implement new reporters (CSV, Slack, Datadog, etc.)
- Enhance existing functionality

#### 3. Documentation
- Improve README and guides
- Add code examples
- Fix typos and clarify explanations
- Add missing docstrings

#### 4. Tests
- Increase test coverage
- Add integration tests
- Improve test reliability

#### 5. Performance Improvements
- Optimize slow code paths
- Reduce memory usage
- Improve parallel execution

### Before You Start

1. **Check existing issues** - See if someone is already working on it
2. **Create an issue** - For significant changes, discuss your approach first
3. **Get feedback** - Maintainers can provide guidance early on

## Pull Request Process

### 1. Create a Feature Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write clear, concise code
- Follow coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add: Brief description of what you added"
# or
git commit -m "Fix: Brief description of bug fix"
# or
git commit -m "Docs: Update contributing guidelines"
```

**Commit message prefixes:**
- `Add:` - New features or functionality
- `Fix:` - Bug fixes
- `Update:` - Updates to existing features
- `Docs:` - Documentation changes
- `Test:` - Test additions or modifications
- `Refactor:` - Code refactoring without feature changes
- `Style:` - Code style/formatting changes
- `Perf:` - Performance improvements

### 4. Run Tests and Linters

```bash
# Format code
black judge_llm
ruff check judge_llm --fix

# Run tests
pytest

# Run specific test markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then:
1. Go to the GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template with:
   - Clear description of changes
   - Related issue numbers (e.g., "Fixes #123")
   - Testing performed
   - Screenshots (if UI changes)

### 6. Code Review Process

- Maintainers will review your PR
- Address any requested changes
- Keep your branch updated with main:
  ```bash
  git fetch upstream
  git rebase upstream/main
  git push origin feature/your-feature-name --force
  ```

### 7. Merge

Once approved, maintainers will merge your PR. Thank you for your contribution!

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (configured in pyproject.toml)
- **Formatter**: Black (automatic formatting)
- **Linter**: Ruff (checks for code quality)

### Code Organization

```python
# Import order (enforced by Ruff)
# 1. Standard library imports
import os
import sys
from typing import Any, Dict, List, Optional

# 2. Third-party imports
import yaml
from pydantic import BaseModel

# 3. Local application imports
from judge_llm.core.models import EvalCase
from judge_llm.providers.base import BaseProvider
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `BaseProvider`, `ResponseEvaluator`)
- **Functions/Methods**: `snake_case` (e.g., `execute_case`, `load_config`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`, `MAX_WORKERS`)
- **Private members**: Prefix with `_` (e.g., `_internal_method`)

### Docstrings

Use Google-style docstrings:

```python
def execute(self, eval_case: EvalCase) -> ProviderResult:
    """Execute evaluation case using the provider.

    Args:
        eval_case: The evaluation case to execute

    Returns:
        ProviderResult containing conversation history and metadata

    Raises:
        ValueError: If eval_case is invalid
        RuntimeError: If execution fails
    """
    pass
```

### Type Hints

Always use type hints for function signatures:

```python
def process_data(data: Dict[str, Any], threshold: float = 0.8) -> List[str]:
    """Process data with the given threshold."""
    pass
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                  # Unit tests for individual components
│   ├── test_providers.py
│   ├── test_evaluators.py
│   └── test_reporters.py
└── integration/           # End-to-end integration tests
    ├── test_cli.py
    └── test_evaluation_flow.py
```

### Writing Tests

#### Unit Tests

```python
import pytest
from judge_llm.providers.mock import MockProvider

class TestMockProvider:
    """Unit tests for MockProvider."""

    def test_initialization(self):
        """Test provider initializes correctly."""
        provider = MockProvider(agent_id="test")
        assert provider.agent_id == "test"

    def test_execute_success(self, sample_eval_case):
        """Test successful execution."""
        provider = MockProvider(agent_id="test")
        result = provider.execute(sample_eval_case)
        assert result.success is True
        assert len(result.conversation_history) > 0
```

#### Integration Tests

```python
import pytest
from judge_llm import evaluate

@pytest.mark.integration
def test_end_to_end_evaluation(tmp_path):
    """Test complete evaluation flow."""
    config = {
        "dataset": {"loader": "local_file", "paths": ["test_data.json"]},
        "providers": [{"type": "mock", "agent_id": "test"}],
        "evaluators": [{"type": "response_evaluator"}],
        "reporters": [{"type": "console"}]
    }

    report = evaluate(**config)
    assert report.total_cases > 0
    assert report.success_rate >= 0.0
```

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_function():
    """Unit test example."""
    pass

@pytest.mark.integration
def test_integration_flow():
    """Integration test example."""
    pass

@pytest.mark.slow
def test_long_running():
    """Slow test example."""
    pass

@pytest.mark.requires_api
def test_api_call():
    """Test requiring API access."""
    pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=judge_llm --cov-report=html

# Run specific markers
pytest -m unit
pytest -m "integration and not slow"

# Run specific test file
pytest tests/unit/test_providers.py

# Run specific test
pytest tests/unit/test_providers.py::TestMockProvider::test_initialization
```

### Test Coverage

- Aim for **80%+ coverage** for new code
- All new features must include tests
- Bug fixes should include regression tests

## Documentation

### Code Documentation

- Add docstrings to all public classes and functions
- Include type hints in function signatures
- Document complex logic with inline comments
- Keep comments up-to-date with code changes

### Example Documentation

When adding new features, include examples:

```bash
examples/
└── 10-your-feature/
    ├── README.md           # Feature overview and instructions
    ├── config.yaml         # Configuration example
    ├── sample.evalset.yaml # Sample dataset
    └── run_evaluation.py   # Python API example
```

### README Updates

Update the main README.md when:
- Adding new providers, evaluators, or reporters
- Changing installation instructions
- Adding new examples
- Modifying configuration options

## Issue Reporting

### Creating Good Issues

When reporting bugs or requesting features:

**Bug Reports:**
```markdown
**Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What you expected to happen

**Actual Behavior:**
What actually happened

**Environment:**
- OS: macOS 14.0
- Python: 3.9.6
- Judge LLM: 1.0.0

**Additional Context:**
Any other relevant information
```

**Feature Requests:**
```markdown
**Problem Statement:**
What problem does this solve?

**Proposed Solution:**
How should it work?

**Alternatives Considered:**
Other approaches you've considered

**Additional Context:**
Examples, mockups, or references
```

## Component Development Guidelines

### Adding a New Provider

1. Create provider file in `judge_llm/providers/`
2. Extend `BaseProvider` class
3. Implement `execute()` method
4. Add tests in `tests/unit/test_providers.py`
5. Create example in `examples/`
6. Update documentation

Example structure:
```python
from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult

class MyProvider(BaseProvider):
    """Custom provider implementation."""

    def __init__(self, agent_id: str, **kwargs):
        super().__init__(agent_id, **kwargs)
        # Initialize your provider

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """Execute evaluation case."""
        # Your implementation
        pass
```

### Adding a New Evaluator

Follow similar pattern for evaluators:
1. Extend `BaseEvaluator`
2. Implement `evaluate()` method
3. Add configuration schema
4. Include tests and examples

### Adding a New Reporter

Follow similar pattern for reporters:
1. Extend `BaseReporter`
2. Implement `generate()` method
3. Handle output formatting
4. Include tests and examples

## License

By contributing to Judge LLM, you agree that your contributions will be licensed under the **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International) license.

Key points:
- Your contributions must be your original work
- By submitting a PR, you grant rights under CC BY-NC-SA 4.0
- All contributions remain open source under the same license
- Commercial use requires separate licensing

For commercial licensing inquiries, contact the maintainers.

## Questions?

If you have questions about contributing:
- Check existing issues and discussions
- Create a new issue with the "question" label
- Reach out to maintainers

---

**Happy Contributing!** 🎉
