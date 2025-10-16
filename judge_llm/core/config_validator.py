"""Configuration validator singleton"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from judge_llm.utils.logger import get_logger


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

    def validate(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate configuration

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
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
            self.logger.info("Configuration validation passed")
        else:
            self.logger.error(f"Configuration validation failed with {len(errors)} errors")
            for error in errors:
                self.logger.error(f"  - {error}")

        return is_valid, errors

    def _validate_agent_config(self, agent_config: Dict[str, Any]) -> List[str]:
        """Validate agent configuration"""
        errors = []

        # Validate num_runs
        num_runs = agent_config.get("num_runs", 1)
        if not isinstance(num_runs, int) or num_runs < 1:
            errors.append(f"agent.num_runs must be a positive integer, got: {num_runs}")

        # Validate parallel_execution
        parallel_execution = agent_config.get("parallel_execution", False)
        if not isinstance(parallel_execution, bool):
            errors.append(
                f"agent.parallel_execution must be a boolean, got: {parallel_execution}"
            )

        # Validate max_workers
        max_workers = agent_config.get("max_workers", 4)
        if not isinstance(max_workers, int) or max_workers < 1:
            errors.append(f"agent.max_workers must be a positive integer, got: {max_workers}")

        # Validate log_level
        log_level = agent_config.get("log_level", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level.upper() not in valid_levels:
            errors.append(
                f"agent.log_level must be one of {valid_levels}, got: {log_level}"
            )

        return errors

    def _validate_dataset_config(self, dataset_config: Dict[str, Any]) -> List[str]:
        """Validate dataset configuration"""
        errors = []

        if not dataset_config:
            errors.append("dataset configuration is required")
            return errors

        # Validate loader type
        loader = dataset_config.get("loader")
        if not loader:
            errors.append("dataset.loader is required")

        # Validate paths
        paths = dataset_config.get("paths", [])
        if not paths:
            errors.append("dataset.paths is required and cannot be empty")
        elif not isinstance(paths, list):
            errors.append(f"dataset.paths must be a list, got: {type(paths)}")
        else:
            for path in paths:
                if not isinstance(path, str):
                    errors.append(f"dataset.paths must contain strings, got: {type(path)}")
                    continue

                # Check if path exists
                path_obj = Path(path).expanduser().resolve()
                if not path_obj.exists():
                    errors.append(f"dataset path does not exist: {path}")

        return errors

    def _validate_providers_config(self, providers_config: List[Dict[str, Any]]) -> List[str]:
        """Validate providers configuration"""
        errors = []

        if not providers_config:
            errors.append("At least one provider must be configured")
            return errors

        if not isinstance(providers_config, list):
            errors.append(f"providers must be a list, got: {type(providers_config)}")
            return errors

        for idx, provider in enumerate(providers_config):
            if not isinstance(provider, dict):
                errors.append(f"providers[{idx}] must be a dictionary")
                continue

            # Validate provider type
            provider_type = provider.get("type")
            if not provider_type:
                errors.append(f"providers[{idx}].type is required")

            # Validate agent_id
            agent_id = provider.get("agent_id")
            if not agent_id:
                errors.append(f"providers[{idx}].agent_id is required")

            # Validate agent_config_path
            agent_config_path = provider.get("agent_config_path")
            if agent_config_path:
                path_obj = Path(agent_config_path).expanduser().resolve()
                if not path_obj.exists():
                    errors.append(
                        f"providers[{idx}].agent_config_path does not exist: {agent_config_path}"
                    )

        return errors

    def _validate_evaluators_config(self, evaluators_config: List[Dict[str, Any]]) -> List[str]:
        """Validate evaluators configuration"""
        errors = []

        if not evaluators_config:
            errors.append("At least one evaluator must be configured")
            return errors

        if not isinstance(evaluators_config, list):
            errors.append(f"evaluators must be a list, got: {type(evaluators_config)}")
            return errors

        for idx, evaluator in enumerate(evaluators_config):
            if not isinstance(evaluator, dict):
                errors.append(f"evaluators[{idx}] must be a dictionary")
                continue

            # Validate evaluator type
            evaluator_type = evaluator.get("type")
            if not evaluator_type:
                errors.append(f"evaluators[{idx}].type is required")
                continue

            # For custom evaluators, validate module_path or module
            if evaluator_type == "custom":
                module_path = evaluator.get("module_path")
                module = evaluator.get("module")

                if not module_path and not module:
                    errors.append(
                        f"evaluators[{idx}]: custom evaluator requires either "
                        "module_path or module"
                    )

                if module_path:
                    path_obj = Path(module_path).expanduser().resolve()
                    if not path_obj.exists():
                        errors.append(
                            f"evaluators[{idx}].module_path does not exist: {module_path}"
                        )
                    elif not path_obj.suffix == ".py":
                        errors.append(
                            f"evaluators[{idx}].module_path must be a Python file: {module_path}"
                        )

                # Validate class_name
                class_name = evaluator.get("class_name")
                if not class_name:
                    errors.append(f"evaluators[{idx}].class_name is required for custom evaluators")

        return errors

    def _validate_reporters_config(self, reporters_config: List[Dict[str, Any]]) -> List[str]:
        """Validate reporters configuration"""
        errors = []

        if not reporters_config:
            # Reporters are optional, default to console
            return errors

        if not isinstance(reporters_config, list):
            errors.append(f"reporters must be a list, got: {type(reporters_config)}")
            return errors

        for idx, reporter in enumerate(reporters_config):
            if not isinstance(reporter, dict):
                errors.append(f"reporters[{idx}] must be a dictionary")
                continue

            # Validate reporter type
            reporter_type = reporter.get("type")
            if not reporter_type:
                errors.append(f"reporters[{idx}].type is required")

            # For file-based reporters, validate output_path directory exists
            if reporter_type in ["html", "json"]:
                output_path = reporter.get("output_path")
                if not output_path:
                    errors.append(f"reporters[{idx}].output_path is required for {reporter_type} reporter")
                else:
                    output_dir = Path(output_path).parent
                    if not output_dir.exists():
                        errors.append(
                            f"reporters[{idx}].output_path directory does not exist: {output_dir}"
                        )

        return errors


def get_validator() -> ConfigValidator:
    """Get the singleton config validator instance

    Returns:
        ConfigValidator instance
    """
    return ConfigValidator()
