"""
Judge LLM - A lightweight LLM evaluation framework
"""

# Load environment variables from .env file if present
from dotenv import load_dotenv
load_dotenv()

from judge_llm.core.evaluate import evaluate
from judge_llm.core.registry import register_evaluator, register_provider, register_reporter
from judge_llm.loaders.base import BaseLoader
from judge_llm.providers.base import BaseProvider
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.reporters.base import BaseReporter
from judge_llm.cli import main

__version__ = "1.0.3"
__all__ = [
    "evaluate",
    "register_evaluator",
    "register_provider",
    "register_reporter",
    "BaseLoader",
    "BaseProvider",
    "BaseEvaluator",
    "BaseReporter",
]
