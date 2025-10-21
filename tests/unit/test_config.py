"""Unit tests for configuration system (loader, validator, merger)."""

import os
import tempfile
from pathlib import Path
import pytest
import yaml

from judge_llm.core.config_loader import ConfigLoader
from judge_llm.core.config_validator import ConfigValidator, ValidationError
from judge_llm.core.config_merger import ConfigMerger


class TestConfigMerger:
    """Test ConfigMerger class."""

    def test_merge_simple_dicts(self):
        """Test merging simple dictionaries."""
        merger = ConfigMerger()
        defaults = {"key1": "value1", "key2": "value2"}
        overrides = {"key2": "override2", "key3": "value3"}

        result = merger.merge(defaults, overrides)

        assert result["key1"] == "value1"
        assert result["key2"] == "override2"
        assert result["key3"] == "value3"

    def test_merge_agent_config(self):
        """Test merging agent configuration."""
        merger = ConfigMerger()
        defaults = {
            "agent": {
                "num_runs": 1,
                "parallel_execution": False,
                "max_workers": 4
            }
        }
        overrides = {
            "agent": {
                "num_runs": 5,
                "parallel_execution": True
            }
        }

        result = merger.merge(defaults, overrides)

        assert result["agent"]["num_runs"] == 5
        assert result["agent"]["parallel_execution"] is True
        assert result["agent"]["max_workers"] == 4  # Kept from defaults

    def test_merge_providers_by_index(self):
        """Test merging providers by index."""
        merger = ConfigMerger()
        defaults = {
            "providers": [
                {"name": "mock", "type": "mock", "config": {"delay": 0}},
                {"name": "gemini", "type": "gemini", "config": {"model": "gemini-1.0"}}
            ]
        }
        overrides = {
            "providers": [
                {"config": {"delay": 100}}
            ]
        }

        result = merger.merge(defaults, overrides)

        # First provider should be merged
        assert result["providers"][0]["name"] == "mock"
        assert result["providers"][0]["config"]["delay"] == 100
        # Second provider unchanged
        assert result["providers"][1]["name"] == "gemini"

    def test_merge_providers_replace_mode(self):
        """Test merging providers with replace mode."""
        merger = ConfigMerger()
        defaults = {
            "providers": [
                {"name": "mock", "type": "mock"}
            ]
        }
        overrides = {
            "providers": [
                {"_merge_mode": "replace", "name": "gemini", "type": "gemini"}
            ]
        }

        result = merger.merge(defaults, overrides)

        # Should only have override provider
        assert len(result["providers"]) == 1
        assert result["providers"][0]["name"] == "gemini"
        assert "_merge_mode" not in result["providers"][0]

    def test_merge_evaluators_by_type(self):
        """Test merging evaluators by type."""
        merger = ConfigMerger()
        defaults = {
            "evaluators": [
                {"type": "response", "config": {"threshold": 0.8}},
                {"type": "cost", "config": {"max_cost": 0.10}}
            ]
        }
        overrides = {
            "evaluators": [
                {"type": "response", "config": {"threshold": 0.9}}
            ]
        }

        result = merger.merge(defaults, overrides)

        # Should have both evaluators
        assert len(result["evaluators"]) == 2
        # Response evaluator threshold updated
        response_eval = [e for e in result["evaluators"] if e["type"] == "response"][0]
        assert response_eval["config"]["threshold"] == 0.9
        # Cost evaluator unchanged
        cost_eval = [e for e in result["evaluators"] if e["type"] == "cost"][0]
        assert cost_eval["config"]["max_cost"] == 0.10

    def test_merge_evaluators_disable(self):
        """Test disabling evaluators."""
        merger = ConfigMerger()
        defaults = {
            "evaluators": [
                {"type": "response", "config": {"threshold": 0.8}},
                {"type": "cost", "config": {"max_cost": 0.10}}
            ]
        }
        overrides = {
            "evaluators": [
                {"type": "response", "enabled": False}
            ]
        }

        result = merger.merge(defaults, overrides)

        # Should only have cost evaluator
        assert len(result["evaluators"]) == 1
        assert result["evaluators"][0]["type"] == "cost"

    def test_merge_evaluators_append_mode(self):
        """Test merging evaluators with append mode."""
        merger = ConfigMerger()
        defaults = {
            "evaluators": [
                {"type": "response", "config": {"threshold": 0.8}}
            ]
        }
        overrides = {
            "evaluators": [
                {"_merge_mode": "append"},
                {"type": "cost", "config": {"max_cost": 0.10}}
            ]
        }

        result = merger.merge(defaults, overrides)

        # Should have both evaluators
        assert len(result["evaluators"]) == 2

    def test_merge_evaluators_replace_mode(self):
        """Test merging evaluators with replace mode."""
        merger = ConfigMerger()
        defaults = {
            "evaluators": [
                {"type": "response", "config": {"threshold": 0.8}},
                {"type": "cost", "config": {"max_cost": 0.10}}
            ]
        }
        overrides = {
            "evaluators": [
                {"_merge_mode": "replace", "type": "latency", "config": {"max_latency": 5.0}}
            ]
        }

        result = merger.merge(defaults, overrides)

        # Should only have latency evaluator
        assert len(result["evaluators"]) == 1
        assert result["evaluators"][0]["type"] == "latency"

    def test_merge_evaluators_empty_list(self):
        """Test merging with empty evaluators list."""
        merger = ConfigMerger()
        defaults = {
            "evaluators": [
                {"type": "response", "config": {"threshold": 0.8}}
            ]
        }
        overrides = {
            "evaluators": []
        }

        result = merger.merge(defaults, overrides)

        # Empty list should disable all evaluators
        assert len(result["evaluators"]) == 0

    def test_merge_reporters_replace(self):
        """Test merging reporters (default replace behavior)."""
        merger = ConfigMerger()
        defaults = {
            "reporters": [
                {"type": "console"},
                {"type": "json"}
            ]
        }
        overrides = {
            "reporters": [
                {"type": "html"}
            ]
        }

        result = merger.merge(defaults, overrides)

        # Should only have HTML reporter
        assert len(result["reporters"]) == 1
        assert result["reporters"][0]["type"] == "html"

    def test_merge_reporters_append(self):
        """Test merging reporters with append mode."""
        merger = ConfigMerger()
        defaults = {
            "reporters": [
                {"type": "console"}
            ]
        }
        overrides = {
            "reporters": [
                {"_merge_mode": "append"},
                {"type": "json"}
            ]
        }

        result = merger.merge(defaults, overrides)

        # Should have both reporters
        assert len(result["reporters"]) == 2

    def test_deep_merge_nested_dicts(self):
        """Test deep merging of nested dictionaries."""
        merger = ConfigMerger()
        defaults = {
            "agent": {
                "config": {
                    "level1": {
                        "level2": {
                            "value1": "default",
                            "value2": "default"
                        }
                    }
                }
            }
        }
        overrides = {
            "agent": {
                "config": {
                    "level1": {
                        "level2": {
                            "value1": "override"
                        }
                    }
                }
            }
        }

        result = merger.merge(defaults, overrides)

        # Deep merged values
        assert result["agent"]["config"]["level1"]["level2"]["value1"] == "override"
        assert result["agent"]["config"]["level1"]["level2"]["value2"] == "default"


class TestConfigValidator:
    """Test ConfigValidator class."""

    def test_validate_valid_config(self, temp_dir):
        """Test validation of valid configuration."""
        # Create a test file
        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')

        validator = ConfigValidator()
        config = {
            "agent": {
                "num_runs": 1,
                "parallel_execution": False,
                "max_workers": 4
            },
            "dataset": {
                "loader": "json",
                "paths": [str(test_file)]
            },
            "providers": [
                {"name": "mock", "type": "mock", "agent_id": "test_agent"}
            ],
            "evaluators": [
                {"type": "response", "config": {"threshold": 0.8}}
            ],
            "reporters": [
                {"type": "console"}
            ]
        }

        is_valid, errors = validator.validate(config)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_num_runs(self):
        """Test validation with invalid num_runs."""
        validator = ConfigValidator()
        config = {
            "agent": {
                "num_runs": -1
            }
        }

        is_valid, errors = validator.validate(config)

        assert is_valid is False
        assert any("num_runs" in error.field for error in errors)

    def test_validate_invalid_parallel_execution(self):
        """Test validation with invalid parallel_execution."""
        validator = ConfigValidator()
        config = {
            "agent": {
                "parallel_execution": "yes"  # Should be boolean
            }
        }

        is_valid, errors = validator.validate(config)

        assert is_valid is False
        assert any("parallel_execution" in error.field for error in errors)

    def test_validate_invalid_max_workers(self):
        """Test validation with invalid max_workers."""
        validator = ConfigValidator()
        config = {
            "agent": {
                "max_workers": 0
            }
        }

        is_valid, errors = validator.validate(config)

        assert is_valid is False
        assert any("max_workers" in error.field for error in errors)

    def test_validation_error_structure(self):
        """Test ValidationError structure."""
        error = ValidationError(
            field="agent.num_runs",
            message="Must be positive",
            fix_suggestion="Set num_runs to 1 or higher"
        )

        assert error.field == "agent.num_runs"
        assert error.message == "Must be positive"
        assert error.fix_suggestion == "Set num_runs to 1 or higher"

    def test_validator_singleton(self):
        """Test that ConfigValidator is a singleton."""
        validator1 = ConfigValidator()
        validator2 = ConfigValidator()

        assert validator1 is validator2


class TestConfigLoader:
    """Test ConfigLoader class."""

    def test_load_dict_config(self):
        """Test loading configuration from dictionary."""
        loader = ConfigLoader()
        config = {
            "agent": {"num_runs": 1},
            "dataset": {"path": "test.json"}
        }

        result = loader.load(config, use_defaults=False)

        assert result["agent"]["num_runs"] == 1
        assert result["dataset"]["path"] == "test.json"

    def test_load_yaml_file(self):
        """Test loading configuration from YAML file."""
        loader = ConfigLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"agent": {"num_runs": 5}}, f)
            temp_path = f.name

        try:
            result = loader.load(temp_path, use_defaults=False)
            assert result["agent"]["num_runs"] == 5
        finally:
            os.unlink(temp_path)

    def test_load_with_defaults(self):
        """Test loading configuration with defaults."""
        loader = ConfigLoader()

        # Create temporary defaults file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                "agent": {"num_runs": 1, "parallel_execution": False},
                "evaluators": [{"type": "response", "config": {"threshold": 0.8}}]
            }, f)
            defaults_path = f.name

        # Create config that overrides some values
        config = {
            "agent": {"num_runs": 5},
            "dataset": {"path": "test.json"}
        }

        try:
            result = loader.load(config, use_defaults=True, defaults_path=defaults_path)

            # Check merged values
            assert result["agent"]["num_runs"] == 5  # Overridden
            assert result["agent"]["parallel_execution"] is False  # From defaults
            assert result["dataset"]["path"] == "test.json"  # From config
            assert len(result["evaluators"]) == 1  # From defaults
        finally:
            os.unlink(defaults_path)

    def test_load_without_defaults(self):
        """Test loading configuration without defaults."""
        loader = ConfigLoader()
        config = {
            "agent": {"num_runs": 3}
        }

        result = loader.load(config, use_defaults=False)

        # Should return config as-is
        assert result == config

    def test_load_with_defaults_path_in_config(self):
        """Test loading with defaults path specified in config."""
        loader = ConfigLoader()

        # Create temporary defaults file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"agent": {"num_runs": 10}}, f)
            defaults_path = f.name

        # Config specifies defaults path
        config = {
            "defaults": defaults_path,
            "agent": {"parallel_execution": True}
        }

        try:
            result = loader.load(config, use_defaults=True)

            # Should merge with specified defaults
            assert result["agent"]["num_runs"] == 10  # From defaults
            assert result["agent"]["parallel_execution"] is True  # From config
            assert "defaults" not in result  # Should be removed
        finally:
            os.unlink(defaults_path)

    def test_load_with_no_defaults_found(self):
        """Test loading when no defaults file is found."""
        loader = ConfigLoader()
        config = {
            "agent": {"num_runs": 2}
        }

        # Use non-existent defaults path and disable fallback search
        result = loader.load(config, use_defaults=False)

        # Should return config with only user-provided values (no defaults merged)
        assert result["agent"]["num_runs"] == 2
        # When defaults are disabled, only user config is returned
        assert "agent" in result

    def test_load_with_env_variable(self, monkeypatch):
        """Test loading with JUDGE_LLM_DEFAULTS environment variable."""
        loader = ConfigLoader()

        # Create temporary defaults file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"agent": {"num_runs": 7}}, f)
            defaults_path = f.name

        # Set environment variable
        monkeypatch.setenv("JUDGE_LLM_DEFAULTS", defaults_path)

        config = {
            "agent": {"parallel_execution": True}
        }

        try:
            result = loader.load(config, use_defaults=True)

            # Should merge with defaults from env variable
            assert result["agent"]["num_runs"] == 7  # From defaults
            assert result["agent"]["parallel_execution"] is True  # From config
        finally:
            os.unlink(defaults_path)

    def test_load_yaml_file_not_found(self):
        """Test loading from non-existent YAML file."""
        loader = ConfigLoader()

        with pytest.raises(FileNotFoundError):
            loader.load("/nonexistent/config.yaml", use_defaults=False)

    def test_load_invalid_yaml(self):
        """Test loading from invalid YAML file."""
        loader = ConfigLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: {")
            temp_path = f.name

        try:
            with pytest.raises(yaml.YAMLError):
                loader.load(temp_path, use_defaults=False)
        finally:
            os.unlink(temp_path)
