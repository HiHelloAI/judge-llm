"""
Judge LLM - A lightweight LLM evaluation framework
"""

from judge_llm.core.evaluate import evaluate
from judge_llm.core.registry import register_evaluator, register_provider
from judge_llm.loaders.base import BaseLoader
from judge_llm.providers.base import BaseProvider
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.reporters.base import BaseReporter

__version__ = "0.1.0"
__all__ = [
    "evaluate",
    "register_evaluator",
    "register_provider",
    "BaseLoader",
    "BaseProvider",
    "BaseEvaluator",
    "BaseReporter",
]
