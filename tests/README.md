# Judge LLM Test Suite

Comprehensive test suite for the judge_llm project covering all features and functionalities.

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── unit/                    # Unit tests for individual components
│   ├── test_models.py       # Core Pydantic models tests
│   ├── test_evaluators.py   # All evaluator tests (response, cost, latency, trajectory)
│   ├── test_config.py       # Configuration system tests (loader, validator, merger)
│   ├── test_reporters.py    # Reporter tests (console, json, html, database)
│   ├── test_providers.py    # Provider tests (mock, gemini)
│   └── test_loaders.py      # Dataset loader tests (local file, directory)
├── integration/             # Integration tests
│   ├── test_evaluate.py     # End-to-end evaluation tests
│   └── test_cli.py          # CLI command tests
└── fixtures/                # Test data and fixtures
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/unit/test_models.py
```

### Run specific test class
```bash
pytest tests/unit/test_models.py::TestPart
```

### Run specific test
```bash
pytest tests/unit/test_models.py::TestPart::test_part_with_text
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage
```bash
pytest --cov=judge_llm --cov-report=html
```

### Run only unit tests
```bash
pytest tests/unit/
```

### Run only integration tests
```bash
pytest tests/integration/
```

### Run tests by marker
```bash
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## Test Coverage

The test suite covers:

### Unit Tests

#### Core Models (`test_models.py`)
- ✅ Part model with all field types (text, function_call, thought, etc.)
- ✅ Content model with roles and multiple parts
- ✅ ToolUse model for tool tracking
- ✅ IntermediateData for conversation metadata
- ✅ Invocation for single conversation turns
- ✅ SessionInput with state management
- ✅ EvalCase with per-case configuration
- ✅ EvalSet with multiple cases
- ✅ ExecutionConfig with defaults and validation
- ✅ ProviderResult with cost and latency tracking
- ✅ EvaluatorResult with scores and thresholds
- ✅ ExecutionRun with complete evaluation results
- ✅ EvaluationReport with summary statistics

#### Evaluators (`test_evaluators.py`)
- ✅ **ResponseEvaluator**: Exact, Jaccard, ROUGE, and recall similarity metrics
- ✅ **CostEvaluator**: Cost threshold validation
- ✅ **LatencyEvaluator**: Latency threshold validation
- ✅ **TrajectoryEvaluator**: Tool sequence matching (exact and partial)
- ✅ Per-case configuration overrides
- ✅ Case sensitivity and normalization options
- ✅ Error handling for provider failures

#### Configuration System (`test_config.py`)
- ✅ **ConfigLoader**: YAML file loading, dict configs, defaults search paths
- ✅ **ConfigValidator**: Field validation with helpful error messages
- ✅ **ConfigMerger**: Deep merge with multiple strategies
  - Agent config merging
  - Provider merging (by index, replace mode)
  - Evaluator merging (by type, append/replace modes)
  - Reporter merging (replace, append modes)
- ✅ Environment variable support
- ✅ Per-config defaults path
- ✅ Singleton pattern for validator

#### Reporters (`test_reporters.py`)
- ✅ **ConsoleReporter**: Rich console output
- ✅ **JSONReporter**: JSON file generation and serialization
- ✅ **HTMLReporter**: HTML report with template rendering
- ✅ **DatabaseReporter**: SQLite storage with proper schema
  - Reports table
  - Eval sets table
  - Eval cases table
  - Execution runs table
  - Invocations table
  - Evaluator results table
- ✅ Multiple report storage
- ✅ Query functionality

#### Providers (`test_providers.py`)
- ✅ **MockProvider**: Execution, cost tracking, latency simulation
- ✅ Multi-turn conversations
- ✅ Metadata tracking
- ✅ Deterministic behavior with seeding
- ✅ Provider registry functionality

#### Loaders (`test_loaders.py`)
- ✅ **LocalFileLoader**: JSON file parsing and validation
- ✅ **DirectoryLoader**: Batch loading with pattern matching
- ✅ Complex conversation history loading
- ✅ Per-case evaluator config loading
- ✅ Error handling for invalid files
- ✅ Recursive directory traversal
- ✅ Loader registry functionality

### Integration Tests

#### Evaluate Function (`test_evaluate.py`)
- ✅ End-to-end evaluation with mock provider
- ✅ Multiple evaluators in single run
- ✅ JSON reporter output verification
- ✅ Database reporter output verification
- ✅ Multiple test cases execution
- ✅ Parallel execution mode
- ✅ Per-case configuration overrides
- ✅ Summary statistics generation
- ✅ Error handling for invalid configs

#### CLI Commands (`test_cli.py`)
- ✅ Main CLI entry point
- ✅ `run` command with config files
- ✅ `validate` command for config validation
- ✅ `list` command for available components
- ✅ `dashboard` command for database viewing
- ✅ Flag options (--no-defaults, --version)
- ✅ JSON output generation
- ✅ Error handling for missing/invalid configs

## Writing New Tests

### Example Unit Test
```python
def test_my_feature():
    """Test description."""
    # Arrange
    component = MyComponent(config={"option": "value"})

    # Act
    result = component.do_something()

    # Assert
    assert result == expected_value
```

### Example Integration Test
```python
def test_end_to_end_workflow(temp_dir):
    """Test complete workflow."""
    # Create test data
    test_file = temp_dir / "test.json"
    with open(test_file, "w") as f:
        json.dump(test_data, f)

    # Run evaluation
    config = {...}
    report = evaluate(config)

    # Verify results
    assert report.overall_success is True
```

## Fixtures

Common fixtures available in `conftest.py`:

- `sample_part`: Part instance
- `sample_content`: Content instance
- `sample_invocation`: Invocation instance
- `sample_eval_case`: EvalCase instance
- `sample_eval_set`: EvalSet with multiple cases
- `sample_execution_run`: ExecutionRun instance
- `sample_evaluation_report`: EvaluationReport instance
- `temp_dir`: Temporary directory for test files
- `sample_config_dict`: Sample configuration dictionary
- `sample_eval_set_json`: JSON file with evaluation set
- `sample_config_yaml`: YAML configuration file
- `mock_env_vars`: Helper for setting environment variables

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Use Fixtures**: Leverage shared fixtures for common test data
3. **Clear Names**: Test names should clearly describe what they test
4. **Arrange-Act-Assert**: Follow the AAA pattern for test structure
5. **Edge Cases**: Test boundary conditions and error cases
6. **Deterministic**: Tests should produce consistent results
7. **Fast**: Keep unit tests fast; use markers for slow tests
8. **Documentation**: Include docstrings explaining test purpose

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest --cov=judge_llm --cov-report=xml
```

## Troubleshooting

### Import Errors
Make sure judge_llm is installed in development mode:
```bash
pip install -e .
```

### Missing Dependencies
Install dev dependencies:
```bash
pip install -e ".[dev]"
```

### Database Lock Errors
Clean up test databases:
```bash
find tests -name "*.db" -delete
```

## Coverage Goals

Target coverage: **85%+** for all modules

Check current coverage:
```bash
pytest --cov=judge_llm --cov-report=term-missing
```

Generate HTML coverage report:
```bash
pytest --cov=judge_llm --cov-report=html
open htmlcov/index.html
```
