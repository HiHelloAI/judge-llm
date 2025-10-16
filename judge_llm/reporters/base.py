"""Base reporter interface"""

from abc import ABC, abstractmethod
from judge_llm.core.models import EvaluationReport


class BaseReporter(ABC):
    """Abstract base class for reporters"""

    @abstractmethod
    def generate_report(self, report: EvaluationReport):
        """Generate report from evaluation results

        Args:
            report: EvaluationReport object
        """
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup resources after report generation"""
        pass
