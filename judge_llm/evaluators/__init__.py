"""Evaluators for comparing expected vs actual results"""

from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.evaluators.response_validator import ResponseValidator
from judge_llm.evaluators.trajectory_validator import TrajectoryValidator
from judge_llm.evaluators.cost_evaluator import CostEvaluator
from judge_llm.evaluators.latency_evaluator import LatencyEvaluator
from judge_llm.core.registry import register_evaluator

# Auto-register built-in evaluators
register_evaluator("response_validator", ResponseValidator)
register_evaluator("trajectory_validator", TrajectoryValidator)
register_evaluator("cost_evaluator", CostEvaluator)
register_evaluator("latency_evaluator", LatencyEvaluator)

__all__ = [
    "BaseEvaluator",
    "ResponseValidator",
    "TrajectoryValidator",
    "CostEvaluator",
    "LatencyEvaluator",
]
