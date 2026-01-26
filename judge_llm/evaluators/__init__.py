"""Evaluators for comparing expected vs actual results"""

from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.evaluators.response_evaluator import ResponseEvaluator
from judge_llm.evaluators.trajectory_evaluator import TrajectoryEvaluator
from judge_llm.evaluators.cost_evaluator import CostEvaluator
from judge_llm.evaluators.latency_evaluator import LatencyEvaluator
from judge_llm.evaluators.subagent_evaluator import SubAgentEvaluator
from judge_llm.evaluators.llm_judge_evaluator import LLMJudgeEvaluator
from judge_llm.evaluators.embedding_similarity_evaluator import EmbeddingSimilarityEvaluator
from judge_llm.core.registry import register_evaluator

# Auto-register built-in evaluators
register_evaluator("response_evaluator", ResponseEvaluator)
register_evaluator("trajectory_evaluator", TrajectoryEvaluator)
register_evaluator("cost_evaluator", CostEvaluator)
register_evaluator("latency_evaluator", LatencyEvaluator)
register_evaluator("subagent_evaluator", SubAgentEvaluator)
register_evaluator("llm_judge_evaluator", LLMJudgeEvaluator)
register_evaluator("embedding_similarity_evaluator", EmbeddingSimilarityEvaluator)

__all__ = [
    "BaseEvaluator",
    "ResponseEvaluator",
    "TrajectoryEvaluator",
    "CostEvaluator",
    "LatencyEvaluator",
    "SubAgentEvaluator",
    "LLMJudgeEvaluator",
    "EmbeddingSimilarityEvaluator",
]
