"""Configuration loader with default config support"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from judge_llm.core.config_merger import get_merger
from judge_llm.utils.logger import get_logger


class ConfigLoader:
    """Load configurations with default config support"""

    def __init__(self):
        self.logger = get_logger()
        self.merger = get_merger()

    def load(
        self,
        config: Union[str, Dict[str, Any]],
        use_defaults: bool = True,
        defaults_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Load configuration with optional defaults

        Args:
            config: Configuration file path or dict
            use_defaults: Whether to use default configuration
            defaults_path: Custom path to defaults file (optional)

        Returns:
            Configuration dictionary (merged if defaults used)
        """
        # Load the test/override config
        if isinstance(config, dict):
            override_config = config
        else:
            override_config = self._load_yaml(config)

        # Check if config itself specifies defaults path
        config_defaults_path = override_config.get("defaults")
        if config_defaults_path:
            defaults_path = config_defaults_path
            # Remove from config after using
            override_config.pop("defaults", None)

        # If not using defaults, return config as-is
        if not use_defaults:
            self.logger.debug("Skipping default configuration")
            return override_config

        # Load defaults
        default_config = self._load_defaults(defaults_path)

        if not default_config:
            # No defaults found, return override config
            self.logger.debug("No default configuration found, using config as-is")
            return override_config

        # Merge defaults with overrides
        self.logger.info("Merging default configuration with test configuration")
        merged_config = self.merger.merge(default_config, override_config)

        return merged_config

    def _load_defaults(self, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load default configuration

        Search order:
        1. Custom path (if provided)
        2. Environment variable JUDGE_LLM_DEFAULTS
        3. Project directory .judge_llm.defaults.yaml
        4. User home ~/.judge_llm/defaults.yaml
        5. None (no defaults)

        Args:
            custom_path: Custom path to defaults file

        Returns:
            Default configuration dict or None if not found
        """
        search_paths = []

        # 1. Custom path
        if custom_path:
            search_paths.append(Path(custom_path).expanduser().resolve())

        # 2. Environment variable
        env_path = os.environ.get("JUDGE_LLM_DEFAULTS")
        if env_path:
            search_paths.append(Path(env_path).expanduser().resolve())

        # 3. Project directory
        project_defaults = Path.cwd() / ".judge_llm.defaults.yaml"
        search_paths.append(project_defaults)

        # 4. User home
        home_defaults = Path.home() / ".judge_llm" / "defaults.yaml"
        search_paths.append(home_defaults)

        # Search for defaults file
        for path in search_paths:
            if path.exists() and path.is_file():
                self.logger.info(f"Loading default configuration from {path}")
                return self._load_yaml(str(path))

        self.logger.debug("No default configuration file found")
        return None

    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load YAML file

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML as dictionary
        """
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        return config or {}


def get_loader() -> ConfigLoader:
    """Get config loader instance

    Returns:
        ConfigLoader instance
    """
    return ConfigLoader()
