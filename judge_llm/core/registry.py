"""Singleton registries for providers, evaluators, and reporters"""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Type
from judge_llm.utils.logger import get_logger


class ProviderRegistry:
    """Singleton registry for LLM providers"""

    _instance = None
    _providers: Dict[str, Type] = {}

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

    def register(self, name: str, provider_class: Type):
        """Register a provider

        Args:
            name: Provider name
            provider_class: Provider class
        """
        self._providers[name] = provider_class
        self.logger.debug(f"Registered provider: {name}")

    def get(self, name: str) -> Optional[Type]:
        """Get a provider class by name

        Args:
            name: Provider name

        Returns:
            Provider class or None if not found
        """
        return self._providers.get(name)

    def list_providers(self) -> list:
        """List all registered providers

        Returns:
            List of provider names
        """
        return list(self._providers.keys())

    def has(self, name: str) -> bool:
        """Check if provider is registered

        Args:
            name: Provider name

        Returns:
            True if provider is registered
        """
        return name in self._providers


class EvaluatorRegistry:
    """Singleton registry for evaluators"""

    _instance = None
    _evaluators: Dict[str, Type] = {}

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

    def register(self, name: str, evaluator_class: Type):
        """Register an evaluator

        Args:
            name: Evaluator name
            evaluator_class: Evaluator class
        """
        self._evaluators[name] = evaluator_class
        self.logger.debug(f"Registered evaluator: {name}")

    def get(self, name: str) -> Optional[Type]:
        """Get an evaluator class by name

        Args:
            name: Evaluator name

        Returns:
            Evaluator class or None if not found
        """
        return self._evaluators.get(name)

    def list_evaluators(self) -> list:
        """List all registered evaluators

        Returns:
            List of evaluator names
        """
        return list(self._evaluators.keys())

    def has(self, name: str) -> bool:
        """Check if evaluator is registered

        Args:
            name: Evaluator name

        Returns:
            True if evaluator is registered
        """
        return name in self._evaluators

    def load_custom_evaluator(self, module_path: str, class_name: str) -> Type:
        """Load a custom evaluator from a Python file

        Args:
            module_path: Path to the Python file
            class_name: Name of the evaluator class

        Returns:
            Evaluator class

        Raises:
            ImportError: If the module cannot be loaded
            AttributeError: If the class is not found in the module
        """
        self.logger.info(f"Loading custom evaluator {class_name} from {module_path}")

        path = Path(module_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Module file not found: {module_path}")

        if not path.suffix == ".py":
            raise ValueError(f"Module path must be a Python file: {module_path}")

        # Create a unique module name
        module_name = f"custom_evaluator_{path.stem}_{id(path)}"

        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Get the class
        if not hasattr(module, class_name):
            raise AttributeError(f"Class {class_name} not found in {module_path}")

        evaluator_class = getattr(module, class_name)

        # Validate that it inherits from BaseEvaluator
        from judge_llm.evaluators.base import BaseEvaluator

        if not issubclass(evaluator_class, BaseEvaluator):
            raise TypeError(
                f"Class {class_name} must inherit from BaseEvaluator"
            )

        self.logger.info(f"Successfully loaded custom evaluator {class_name}")

        return evaluator_class

    def load_custom_evaluator_from_module(self, module_name: str, class_name: str) -> Type:
        """Load a custom evaluator from a Python module

        Args:
            module_name: Python module name (e.g., 'my_package.evaluators')
            class_name: Name of the evaluator class

        Returns:
            Evaluator class

        Raises:
            ImportError: If the module cannot be loaded
            AttributeError: If the class is not found in the module
        """
        self.logger.info(f"Loading custom evaluator {class_name} from module {module_name}")

        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            raise ImportError(f"Cannot import module {module_name}: {e}")

        if not hasattr(module, class_name):
            raise AttributeError(f"Class {class_name} not found in module {module_name}")

        evaluator_class = getattr(module, class_name)

        # Validate that it inherits from BaseEvaluator
        from judge_llm.evaluators.base import BaseEvaluator

        if not issubclass(evaluator_class, BaseEvaluator):
            raise TypeError(
                f"Class {class_name} must inherit from BaseEvaluator"
            )

        self.logger.info(f"Successfully loaded custom evaluator {class_name}")

        return evaluator_class


class ReporterRegistry:
    """Singleton registry for reporters"""

    _instance = None
    _reporters: Dict[str, Type] = {}

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

    def register(self, name: str, reporter_class: Type):
        """Register a reporter

        Args:
            name: Reporter name
            reporter_class: Reporter class
        """
        self._reporters[name] = reporter_class
        self.logger.debug(f"Registered reporter: {name}")

    def get(self, name: str) -> Optional[Type]:
        """Get a reporter class by name

        Args:
            name: Reporter name

        Returns:
            Reporter class or None if not found
        """
        return self._reporters.get(name)

    def list_reporters(self) -> list:
        """List all registered reporters

        Returns:
            List of reporter names
        """
        return list(self._reporters.keys())

    def has(self, name: str) -> bool:
        """Check if reporter is registered

        Args:
            name: Reporter name

        Returns:
            True if reporter is registered
        """
        return name in self._reporters

    def load_custom_reporter(self, module_path: str, class_name: str) -> Type:
        """Load a custom reporter from a Python file

        Args:
            module_path: Path to the Python file
            class_name: Name of the reporter class

        Returns:
            Reporter class

        Raises:
            ImportError: If the module cannot be loaded
            AttributeError: If the class is not found in the module
        """
        self.logger.info(f"Loading custom reporter {class_name} from {module_path}")

        path = Path(module_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Module file not found: {module_path}")

        if not path.suffix == ".py":
            raise ValueError(f"Module path must be a Python file: {module_path}")

        # Create a unique module name
        module_name = f"custom_reporter_{path.stem}_{id(path)}"

        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Get the class
        if not hasattr(module, class_name):
            raise AttributeError(f"Class {class_name} not found in {module_path}")

        reporter_class = getattr(module, class_name)

        # Validate that it inherits from BaseReporter
        from judge_llm.reporters.base import BaseReporter

        if not issubclass(reporter_class, BaseReporter):
            raise TypeError(
                f"Class {class_name} must inherit from BaseReporter"
            )

        self.logger.info(f"Successfully loaded custom reporter {class_name}")

        return reporter_class

    def load_custom_reporter_from_module(self, module_name: str, class_name: str) -> Type:
        """Load a custom reporter from a Python module

        Args:
            module_name: Python module name (e.g., 'my_package.reporters')
            class_name: Name of the reporter class

        Returns:
            Reporter class

        Raises:
            ImportError: If the module cannot be loaded
            AttributeError: If the class is not found in the module
        """
        self.logger.info(f"Loading custom reporter {class_name} from module {module_name}")

        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            raise ImportError(f"Cannot import module {module_name}: {e}")

        if not hasattr(module, class_name):
            raise AttributeError(f"Class {class_name} not found in module {module_name}")

        reporter_class = getattr(module, class_name)

        # Validate that it inherits from BaseReporter
        from judge_llm.reporters.base import BaseReporter

        if not issubclass(reporter_class, BaseReporter):
            raise TypeError(
                f"Class {class_name} must inherit from BaseReporter"
            )

        self.logger.info(f"Successfully loaded custom reporter {class_name}")

        return reporter_class


def get_provider_registry() -> ProviderRegistry:
    """Get the singleton provider registry instance

    Returns:
        ProviderRegistry instance
    """
    return ProviderRegistry()


def get_evaluator_registry() -> EvaluatorRegistry:
    """Get the singleton evaluator registry instance

    Returns:
        EvaluatorRegistry instance
    """
    return EvaluatorRegistry()


def register_provider(name: str, provider_class: Type):
    """Register a provider

    Args:
        name: Provider name
        provider_class: Provider class
    """
    registry = get_provider_registry()
    registry.register(name, provider_class)


def register_evaluator(name: str, evaluator_class: Type):
    """Register an evaluator

    Args:
        name: Evaluator name
        evaluator_class: Evaluator class
    """
    registry = get_evaluator_registry()
    registry.register(name, evaluator_class)


def get_reporter_registry() -> ReporterRegistry:
    """Get the singleton reporter registry instance

    Returns:
        ReporterRegistry instance
    """
    return ReporterRegistry()


def register_reporter(name: str, reporter_class: Type):
    """Register a reporter

    Args:
        name: Reporter name
        reporter_class: Reporter class
    """
    registry = get_reporter_registry()
    registry.register(name, reporter_class)
