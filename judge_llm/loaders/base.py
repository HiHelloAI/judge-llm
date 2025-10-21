"""Base loader interface"""

from abc import ABC, abstractmethod
from typing import List
from judge_llm.core.models import EvalSet


class BaseLoader(ABC):
    """Abstract base class for data loaders"""

    @abstractmethod
    def load(self) -> List[EvalSet]:
        """Load evaluation sets

        Returns:
            List of EvalSet objects
        """
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup resources after loading"""
        pass
