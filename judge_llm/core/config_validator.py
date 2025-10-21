"""Configuration validator singleton"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, NamedTuple
from judge_llm.utils.logger import get_logger


class ValidationError(NamedTuple):
    """Structured validation error with helpful fix suggestion"""
    field: str
    message: str
    fix_suggestion: str


class ConfigValidator:
    """Singleton configuration validator"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.logger = get_logger()
        self._initialized = True

    def validate(self, config: Dict[str, Any]) -> tuple[bool, List[ValidationError]]:
        """Validate configuration

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, list_of_validation_errors)
        """
        errors = []

        self.logger.debug("Starting configuration validation")

        # Validate agent section
        errors.extend(self._validate_agent_config(config.get("agent", {})))

        # Validate dataset section
        errors.extend(self._validate_dataset_config(config.get("dataset", {})))

        # Validate providers section
        errors.extend(self._validate_providers_config(config.get("providers", [])))

        # Validate evaluators section
        errors.extend(self._validate_evaluators_config(config.get("evaluators", [])))

        # Validate reporters section
        errors.extend(self._validate_reporters_config(config.get("reporters", [])))

        is_valid = len(errors) == 0

        if is_valid:
            self.logger.info("✓ Configuration validation passed")
        else:
            self.logger.error(f"✗ Configuration validation failed with {len(errors)} error(s)")

        return is_valid, errors

    def _validate_agent_config(self, agent_config: Dict[str, Any]) -> List[ValidationError]:
        """Validate agent configuration"""
        errors = []

        # Validate num_runs
        num_runs = agent_config.get("num_runs", 1)
        if not isinstance(num_runs, int) or num_runs < 1:
            errors.append(ValidationError(
                field="agent.num_runs",
                message=f"Must be a positive integer, got: {num_runs}",
                fix_suggestion="Set 'num_runs: 1' or higher in the agent section"
            ))

        # Validate parallel_execution
        parallel_execution = agent_config.get("parallel_execution", False)
        if not isinstance(parallel_execution, bool):
            errors.append(ValidationError(
                field="agent.parallel_execution",
                message=f"Must be a boolean, got: {parallel_execution}",
                fix_suggestion="Set 'parallel_execution: true' or 'parallel_execution: false'"
            ))

        # Validate max_workers
        max_workers = agent_config.get("max_workers", 4)
        if not isinstance(max_workers, int) or max_workers < 1:
            errors.append(ValidationError(
                field="agent.max_workers",
                message=f"Must be a positive integer, got: {max_workers}",
                fix_suggestion="Set 'max_workers: 4' or another positive number"
            ))

        # Validate log_level
        log_level = agent_config.get("log_level", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level.upper() not in valid_levels:
            errors.append(ValidationError(
                field="agent.log_level",
                message=f"Must be one of {valid_levels}, got: {log_level}",
                fix_suggestion=f"Set 'log_level: INFO' or choose from: {', '.join(valid_levels)}"
            ))

        return errors

    def _validate_dataset_config(self, dataset_config: Dict[str, Any]) -> List[ValidationError]:
        """Validate dataset configuration"""
        errors = []

        if not dataset_config:
            errors.append(ValidationError(
                field="dataset",
                message="Dataset configuration is required",
                fix_suggestion="Add a 'dataset:' section with 'loader' and 'paths' fields"
            ))
            return errors

        # Validate loader type
        loader = dataset_config.get("loader")
        if not loader:
            errors.append(ValidationError(
                field="dataset.loader",
                message="Loader type is required",
                fix_suggestion="Add 'loader: json' to your dataset configuration"
            ))

        # Validate paths
        paths = dataset_config.get("paths", [])
        if not paths:
            errors.append(ValidationError(
                field="dataset.paths",
                message="Paths list is required and cannot be empty",
                fix_suggestion="Add 'paths: [\"path/to/dataset.json\"]' to your dataset configuration"
            ))
        elif not isinstance(paths, list):
            errors.append(ValidationError(
                field="dataset.paths",
                message=f"Must be a list, got: {type(paths).__name__}",
                fix_suggestion="Change paths to a list format, e.g., 'paths: [\"file1.json\", \"file2.json\"]'"
            ))
        else:
            for idx, path in enumerate(paths):
                if not isinstance(path, str):
                    errors.append(ValidationError(
                        field=f"dataset.paths[{idx}]",
                        message=f"Must be a string, got: {type(path).__name__}",
                        fix_suggestion=f"Ensure all paths are strings in quotes"
                    ))
                    continue

                # Check if path exists
                path_obj = Path(path).expanduser().resolve()
                if not path_obj.exists():
                    errors.append(ValidationError(
                        field=f"dataset.paths[{idx}]",
                        message=f"File does not exist: {path}",
                        fix_suggestion=f"Create the file '{path}' or update the path to an existing file"
                    ))

        return errors

    def _validate_providers_config(self, providers_config: List[Dict[str, Any]]) -> List[ValidationError]:
        """Validate providers configuration"""
        errors = []

        if not providers_config:
            errors.append(ValidationError(
                field="providers",
                message="At least one provider must be configured",
                fix_suggestion="Add a provider, e.g., '- type: gemini\\n  agent_id: your-agent-id'"
            ))
            return errors

        if not isinstance(providers_config, list):
            errors.append(ValidationError(
                field="providers",
                message=f"Must be a list, got: {type(providers_config).__name__}",
                fix_suggestion="Format providers as a YAML list using '- type: ...' syntax"
            ))
            return errors

        for idx, provider in enumerate(providers_config):
            if not isinstance(provider, dict):
                errors.append(ValidationError(
                    field=f"providers[{idx}]",
                    message="Must be a dictionary",
                    fix_suggestion="Each provider should have fields like 'type' and 'agent_id'"
                ))
                continue

            # Validate provider type
            provider_type = provider.get("type")
            if not provider_type:
                errors.append(ValidationError(
                    field=f"providers[{idx}].type",
                    message="Provider type is required",
                    fix_suggestion="Add 'type: gemini' or another supported provider type"
                ))

            # Validate agent_id
            agent_id = provider.get("agent_id")
            if not agent_id:
                errors.append(ValidationError(
                    field=f"providers[{idx}].agent_id",
                    message="Agent ID is required",
                    fix_suggestion="Add 'agent_id: your-agent-identifier' to the provider configuration"
                ))

            # Validate agent_config_path
            agent_config_path = provider.get("agent_config_path")
            if agent_config_path:
                path_obj = Path(agent_config_path).expanduser().resolve()
                if not path_obj.exists():
                    errors.append(ValidationError(
                        field=f"providers[{idx}].agent_config_path",
                        message=f"File does not exist: {agent_config_path}",
                        fix_suggestion=f"Create the config file '{agent_config_path}' or update the path"
                    ))

        return errors

    def _validate_evaluators_config(self, evaluators_config: List[Dict[str, Any]]) -> List[ValidationError]:
        """Validate evaluators configuration"""
        errors = []

        if not evaluators_config:
            errors.append(ValidationError(
                field="evaluators",
                message="At least one evaluator must be configured",
                fix_suggestion="Add an evaluator, e.g., '- type: llm_grader\\n  name: response_quality'"
            ))
            return errors

        if not isinstance(evaluators_config, list):
            errors.append(ValidationError(
                field="evaluators",
                message=f"Must be a list, got: {type(evaluators_config).__name__}",
                fix_suggestion="Format evaluators as a YAML list using '- type: ...' syntax"
            ))
            return errors

        for idx, evaluator in enumerate(evaluators_config):
            if not isinstance(evaluator, dict):
                errors.append(ValidationError(
                    field=f"evaluators[{idx}]",
                    message="Must be a dictionary",
                    fix_suggestion="Each evaluator should have fields like 'type' and 'name'"
                ))
                continue

            # Validate evaluator type
            evaluator_type = evaluator.get("type")
            if not evaluator_type:
                errors.append(ValidationError(
                    field=f"evaluators[{idx}].type",
                    message="Evaluator type is required",
                    fix_suggestion="Add 'type: llm_grader', 'type: exact_match', or 'type: custom'"
                ))
                continue

            # For custom evaluators, validate module_path or module
            if evaluator_type == "custom":
                module_path = evaluator.get("module_path")
                module = evaluator.get("module")

                if not module_path and not module:
                    errors.append(ValidationError(
                        field=f"evaluators[{idx}]",
                        message="Custom evaluator requires either 'module_path' or 'module'",
                        fix_suggestion="Add 'module_path: path/to/evaluator.py' or 'module: your_module'"
                    ))

                if module_path:
                    path_obj = Path(module_path).expanduser().resolve()
                    if not path_obj.exists():
                        errors.append(ValidationError(
                            field=f"evaluators[{idx}].module_path",
                            message=f"File does not exist: {module_path}",
                            fix_suggestion=f"Create '{module_path}' or update to the correct path"
                        ))
                    elif not path_obj.suffix == ".py":
                        errors.append(ValidationError(
                            field=f"evaluators[{idx}].module_path",
                            message=f"Must be a Python file (.py), got: {module_path}",
                            fix_suggestion="Update the path to point to a .py file"
                        ))

                # Validate class_name
                class_name = evaluator.get("class_name")
                if not class_name:
                    errors.append(ValidationError(
                        field=f"evaluators[{idx}].class_name",
                        message="class_name is required for custom evaluators",
                        fix_suggestion="Add 'class_name: YourEvaluatorClass' to the custom evaluator"
                    ))

        return errors

    def _validate_reporters_config(self, reporters_config: List[Dict[str, Any]]) -> List[ValidationError]:
        """Validate reporters configuration"""
        errors = []

        if not reporters_config:
            # Reporters are optional, default to console
            return errors

        if not isinstance(reporters_config, list):
            errors.append(ValidationError(
                field="reporters",
                message=f"Must be a list, got: {type(reporters_config).__name__}",
                fix_suggestion="Format reporters as a YAML list using '- type: ...' syntax"
            ))
            return errors

        for idx, reporter in enumerate(reporters_config):
            if not isinstance(reporter, dict):
                errors.append(ValidationError(
                    field=f"reporters[{idx}]",
                    message="Must be a dictionary",
                    fix_suggestion="Each reporter should have a 'type' field"
                ))
                continue

            # Validate reporter type
            reporter_type = reporter.get("type")
            if not reporter_type:
                errors.append(ValidationError(
                    field=f"reporters[{idx}].type",
                    message="Reporter type is required",
                    fix_suggestion="Add 'type: console', 'type: html', or 'type: json'"
                ))

            # For file-based reporters, validate output_path is provided
            if reporter_type in ["html", "json"]:
                output_path = reporter.get("output_path")
                if not output_path:
                    errors.append(ValidationError(
                        field=f"reporters[{idx}].output_path",
                        message=f"output_path is required for {reporter_type} reporter",
                        fix_suggestion=f"Add 'output_path: reports/report.{reporter_type}' to the reporter"
                    ))
                # Note: Directory will be created automatically by the reporter if it doesn't exist

        return errors


def get_validator() -> ConfigValidator:
    """Get the singleton config validator instance

    Returns:
        ConfigValidator instance
    """
    return ConfigValidator()
