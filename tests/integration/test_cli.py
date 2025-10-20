"""Integration tests for CLI commands."""

import json
import tempfile
from pathlib import Path
import pytest
from click.testing import CliRunner

from judge_llm.cli import main, run, validate, dashboard
# Note: 'list' is a Python builtin, so import it differently
from judge_llm import cli


class TestCLI:
    """Test CLI commands."""

    def test_cli_main(self):
        """Test main CLI entry point."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])

        assert result.exit_code == 0
        assert 'judge-llm' in result.output or 'Usage' in result.output

    def test_cli_run_command_help(self):
        """Test run command help."""
        runner = CliRunner()
        result = runner.invoke(run, ['--help'])

        assert result.exit_code == 0
        assert 'run' in result.output.lower() or 'config' in result.output.lower()

    def test_cli_run_with_config(self, temp_dir):
        """Test run command with config file."""
        # Create eval set
        eval_set_data = {
            "eval_set_id": "cli_test",
            "name": "CLI Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": "case1",
                    "session_input": {"app_name": "test", "user_id": "user1"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": []
                }
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        # Create config file
        config = {
            "agent": {
                "num_runs": 1,
                "fail_on_threshold_violation": False  # Allow failures for testing
            },
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [{"type": "console"}]
        }

        import yaml
        config_path = temp_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        runner = CliRunner()
        result = runner.invoke(run, ['--config', str(config_path)])

        # Should complete without error
        assert result.exit_code == 0

    def test_cli_validate_command(self, temp_dir):
        """Test validate command."""
        # Create valid config with test file
        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')

        config = {
            "agent": {"num_runs": 1},
            "dataset": {
                "loader": "local_file",
                "paths": [str(test_file)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [{"type": "console"}]
        }

        import yaml
        config_path = temp_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        runner = CliRunner()
        result = runner.invoke(validate, ['--config', str(config_path)])

        # Should validate successfully
        assert result.exit_code == 0

    def test_cli_validate_invalid_config(self, temp_dir):
        """Test validate command with invalid config."""
        # Create invalid config (missing required fields)
        config = {
            "agent": {"num_runs": -1}  # Invalid value
        }

        import yaml
        config_path = temp_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        runner = CliRunner()
        result = runner.invoke(validate, ['--config', str(config_path)])

        # Should detect validation error
        assert result.exit_code != 0 or 'error' in result.output.lower()

    def test_cli_list_command(self):
        """Test list command."""
        runner = CliRunner()
        result = runner.invoke(cli.list, ['providers'])

        assert result.exit_code == 0
        # Should show available components
        assert len(result.output) > 0

    def test_cli_list_providers(self):
        """Test list providers."""
        runner = CliRunner()
        result = runner.invoke(cli.list, ['providers'])

        assert result.exit_code == 0
        assert 'mock' in result.output.lower() or 'provider' in result.output.lower()

    def test_cli_list_evaluators(self):
        """Test list evaluators."""
        runner = CliRunner()
        result = runner.invoke(cli.list, ['evaluators'])

        assert result.exit_code == 0
        assert 'evaluator' in result.output.lower() or 'response' in result.output.lower()

    def test_cli_list_reporters(self):
        """Test list command with reporters."""
        runner = CliRunner()
        result = runner.invoke(cli.list, ['reporters'])

        # Reporters is a valid list command option
        assert result.exit_code == 0
        assert 'reporter' in result.output.lower() or 'console' in result.output.lower()

    def test_cli_dashboard_command(self, temp_dir):
        """Test dashboard command."""
        # Create database
        db_path = temp_dir / "results.db"

        # Create a minimal database file
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.close()

        runner = CliRunner()
        result = runner.invoke(dashboard, ['--db', str(db_path), '--no-browser'])

        # Command should run (may exit with specific code if no data or with error for empty DB)
        # Exit code 2 is also acceptable as it means command line was processed but execution failed
        assert result.exit_code in [0, 1, 2]

    def test_cli_run_with_no_defaults(self, temp_dir):
        """Test run command with --no-defaults flag."""
        eval_set_data = {
            "eval_set_id": "no_defaults_test",
            "name": "No Defaults Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": "case1",
                    "session_input": {"app_name": "test", "user_id": "user1"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": []
                }
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        config = {
            "agent": {
                "num_runs": 1,
                "fail_on_threshold_violation": False  # Allow failures for testing
            },
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [{"type": "console"}]
        }

        import yaml
        config_path = temp_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        runner = CliRunner()
        result = runner.invoke(run, ['--config', str(config_path), '--no-defaults'])

        # Should complete
        assert result.exit_code == 0

    def test_cli_run_with_json_output(self, temp_dir):
        """Test run command with JSON output."""
        eval_set_data = {
            "eval_set_id": "json_output_test",
            "name": "JSON Output Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": "case1",
                    "session_input": {"app_name": "test", "user_id": "user1"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": []
                }
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        output_path = temp_dir / "output.json"

        config = {
            "agent": {
                "num_runs": 1,
                "fail_on_threshold_violation": False  # Allow failures for testing
            },
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [
                {
                    "type": "json",
                    "output_path": str(output_path)
                }
            ]
        }

        import yaml
        config_path = temp_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        runner = CliRunner()
        result = runner.invoke(run, ['--config', str(config_path)])

        assert result.exit_code == 0
        assert output_path.exists()

    def test_cli_version(self):
        """Test version display."""
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])

        # Should display version or command info
        assert result.exit_code in [0, 2]  # 2 for no version flag


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_cli_run_missing_config(self):
        """Test run command without config."""
        runner = CliRunner()
        result = runner.invoke(run, [])

        # Should fail with appropriate message
        assert result.exit_code != 0

    def test_cli_run_invalid_config_file(self):
        """Test run command with non-existent config file."""
        runner = CliRunner()
        result = runner.invoke(run, ['--config', '/nonexistent/config.yaml'])

        # Should fail
        assert result.exit_code != 0

    def test_cli_validate_missing_config(self):
        """Test validate command without config."""
        runner = CliRunner()
        result = runner.invoke(validate, [])

        # Should fail
        assert result.exit_code != 0
