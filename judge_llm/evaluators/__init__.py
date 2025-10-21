"""Evaluators for comparing expected vs actual results"""

from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.evaluators.response_evaluator import ResponseEvaluator
from judge_llm.evaluators.trajectory_evaluator import TrajectoryEvaluator
from judge_llm.evaluators.cost_evaluator import CostEvaluator
from judge_llm.evaluators.latency_evaluator import LatencyEvaluator
from judge_llm.core.registry import register_evaluator

# Auto-register built-in evaluators
register_evaluator("response_evaluator", ResponseEvaluator)
register_evaluator("trajectory_evaluator", TrajectoryEvaluator)
register_evaluator("cost_evaluator", CostEvaluator)
register_evaluator("latency_evaluator", LatencyEvaluator)

__all__ = [
    "BaseEvaluator",
    "ResponseEvaluator",
    "TrajectoryEvaluator",
    "CostEvaluator",
    "LatencyEvaluator",
]
