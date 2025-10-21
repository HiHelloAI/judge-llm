"""Configuration merger with deep merge and override support"""

from typing import Any, Dict, List, Optional
from judge_llm.utils.logger import get_logger


class ConfigMerger:
    """Merge configurations with deep merge and override strategy"""

    def __init__(self):
        self.logger = get_logger()

    def merge(
        self, defaults: Dict[str, Any], overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge default and override configurations

        Args:
            defaults: Default configuration
            overrides: Override configuration

        Returns:
            Merged configuration
        """
        self.logger.debug("Merging default and override configurations")

        # Start with copy of defaults
        merged = defaults.copy()

        # Merge each section
        for key, value in overrides.items():
            if key not in merged:
                # New key in overrides, add it
                merged[key] = value
            elif key == "agent":
                # Merge agent settings (dict merge)
                merged[key] = self._merge_dicts(merged[key], value)
            elif key == "dataset":
                # Dataset is required in test config, use override
                merged[key] = value
            elif key == "providers":
                # Merge providers list
                merged[key] = self._merge_providers(merged.get(key, []), value)
            elif key == "evaluators":
                # Merge evaluators list
                merged[key] = self._merge_evaluators(merged.get(key, []), value)
            elif key == "reporters":
                # Reporters can be replaced or merged
                merged[key] = self._merge_reporters(merged.get(key, []), value)
            else:
                # For other keys, override completely
                merged[key] = value

        return merged

    def _merge_dicts(
        self, default: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries

        Args:
            default: Default dictionary
            override: Override dictionary

        Returns:
            Merged dictionary
        """
        result = default.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._merge_dicts(result[key], value)
            else:
                # Override value
                result[key] = value

        return result

    def _merge_providers(
        self, defaults: List[Dict[str, Any]], overrides: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge provider configurations

        Strategy:
        - If overrides is empty, use defaults
        - If overrides has _merge_mode: replace, replace all defaults
        - Otherwise, merge by index (first override merges with first default, etc.)

        Args:
            defaults: Default provider list
            overrides: Override provider list

        Returns:
            Merged provider list
        """
        if not overrides:
            return defaults

        # Check for special merge mode
        if len(overrides) > 0 and overrides[0].get("_merge_mode") == "replace":
            # Remove special key and return overrides
            result = []
            for override in overrides:
                provider = override.copy()
                provider.pop("_merge_mode", None)
                result.append(provider)
            return result

        # Merge by index
        merged = []
        max_len = max(len(defaults), len(overrides))

        for i in range(max_len):
            if i < len(defaults) and i < len(overrides):
                # Merge default with override
                merged.append(self._merge_dicts(defaults[i], overrides[i]))
            elif i < len(defaults):
                # Only default exists
                merged.append(defaults[i].copy())
            else:
                # Only override exists
                merged.append(overrides[i].copy())

        return merged

    def _merge_evaluators(
        self, defaults: List[Dict[str, Any]], overrides: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge evaluator configurations

        Strategy:
        - Empty list [] means no evaluators (disable all)
        - _merge_mode: append means add to defaults
        - _merge_mode: replace means replace all defaults
        - Otherwise, merge by type (override specific evaluator by type)

        Args:
            defaults: Default evaluator list
            overrides: Override evaluator list

        Returns:
            Merged evaluator list
        """
        if not overrides:
            # Empty list = no evaluators
            return []

        # Check for special merge mode
        if len(overrides) > 0:
            first_mode = overrides[0].get("_merge_mode")

            if first_mode == "append":
                # Append to defaults
                result = defaults.copy()
                for override in overrides:
                    if "_merge_mode" not in override:
                        result.append(override.copy())
                return result

            elif first_mode == "replace":
                # Replace all defaults
                result = []
                for override in overrides:
                    evaluator = override.copy()
                    evaluator.pop("_merge_mode", None)
                    result.append(evaluator)
                return result

        # Merge by type (default behavior)
        merged = []
        default_by_type = {
            eval.get("type"): eval for eval in defaults if eval.get("type")
        }
        override_by_type = {
            eval.get("type"): eval for eval in overrides if eval.get("type")
        }

        # Start with defaults
        for eval_type, default_eval in default_by_type.items():
            if eval_type in override_by_type:
                # Merge with override
                override_eval = override_by_type[eval_type]

                # If override sets enabled: false, skip this evaluator
                if not override_eval.get("enabled", True):
                    continue

                merged.append(self._merge_dicts(default_eval, override_eval))
            else:
                # Keep default
                merged.append(default_eval.copy())

        # Add new evaluators from overrides
        for eval_type, override_eval in override_by_type.items():
            if eval_type not in default_by_type:
                merged.append(override_eval.copy())

        return merged

    def _merge_reporters(
        self, defaults: List[Dict[str, Any]], overrides: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge reporter configurations

        Strategy:
        - _merge_mode: append means add to defaults
        - _merge_mode: replace means replace all defaults
        - Otherwise, replace defaults with overrides

        Args:
            defaults: Default reporter list
            overrides: Override reporter list

        Returns:
            Merged reporter list
        """
        if not overrides:
            return defaults

        # Check for special merge mode
        if len(overrides) > 0:
            first_mode = overrides[0].get("_merge_mode")

            if first_mode == "append":
                # Append to defaults
                result = defaults.copy()
                for override in overrides:
                    if "_merge_mode" not in override:
                        result.append(override.copy())
                return result

        # Default behavior: replace
        return [r.copy() for r in overrides]


def get_merger() -> ConfigMerger:
    """Get config merger instance

    Returns:
        ConfigMerger instance
    """
    return ConfigMerger()
