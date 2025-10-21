"""Core Pydantic models for Judge LLM framework"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# Eval Set Models (matching the JSON structure)


class Part(BaseModel):
    """Content part in a message"""

    text: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    function_response: Optional[Dict[str, Any]] = None
    thought: Optional[str] = None
    inline_data: Optional[Dict[str, Any]] = None
    file_data: Optional[Dict[str, Any]] = None
    video_metadata: Optional[Dict[str, Any]] = None
    thought_signature: Optional[str] = None
    code_execution_result: Optional[Dict[str, Any]] = None
    executable_code: Optional[Dict[str, Any]] = None


class Content(BaseModel):
    """Content in user or agent messages"""

    parts: List[Part]
    role: Optional[str] = None


class ToolUse(BaseModel):
    """Tool usage information"""

    id: str
    name: str
    args: Dict[str, Any]


class IntermediateResponse(BaseModel):
    """Intermediate agent response"""

    agent_name: str
    parts: List[Part]


class IntermediateData(BaseModel):
    """Intermediate data including tool uses and responses"""

    tool_uses: List[ToolUse] = Field(default_factory=list)
    intermediate_responses: List[Any] = Field(default_factory=list)


class Invocation(BaseModel):
    """Single conversation invocation"""

    invocation_id: str
    user_content: Content
    final_response: Content
    intermediate_data: IntermediateData = Field(default_factory=IntermediateData)
    creation_timestamp: float


class SessionInput(BaseModel):
    """Session input configuration"""

    app_name: str
    user_id: str
    state: Dict[str, Any] = Field(default_factory=dict)
    user_prompt: Optional[str] = None
    system_instruction: Optional[str] = None

    model_config = {"extra": "allow"}  # Allow additional fields


class EvalCase(BaseModel):
    """Single evaluation case"""

    eval_id: str
    conversation: List[Invocation]
    session_input: SessionInput
    creation_timestamp: float
    evaluator_config: Optional[Dict[str, Any]] = Field(default_factory=dict)  # Per-test-case evaluator config


class EvalSet(BaseModel):
    """Evaluation set containing multiple cases"""

    eval_set_id: str
    name: str
    description: Optional[str] = None
    eval_cases: List[EvalCase]
    creation_timestamp: float


# Execution Configuration Models


class ExecutionConfig(BaseModel):
    """Configuration for execution"""

    num_runs: int = 1
    parallel_execution: bool = False
    max_workers: int = 4
    fail_on_threshold_violation: bool = True
    log_level: str = "INFO"


# Provider Result Models


class ProviderResult(BaseModel):
    """Result from a provider execution"""

    conversation_history: List[Invocation]
    cost: float = 0.0
    time_taken: float = 0.0
    token_usage: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


# Evaluator Result Models


class EvaluatorResult(BaseModel):
    """Result from an evaluator"""

    evaluator_name: str
    evaluator_type: str
    success: bool
    score: Optional[float] = None
    threshold: Optional[float] = None
    passed: bool
    details: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# Execution Result Models


class ExecutionRun(BaseModel):
    """Single execution run result"""

    execution_id: str
    run_number: int
    eval_set_id: str
    eval_case_id: str
    provider_type: str
    provider_result: ProviderResult
    evaluator_results: List[EvaluatorResult] = Field(default_factory=list)
    overall_success: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    eval_case: Optional["EvalCase"] = None  # Original eval case with expected responses


class EvaluationReport(BaseModel):
    """Final evaluation report"""

    execution_runs: List[ExecutionRun]
    summary: Dict[str, Any] = Field(default_factory=dict)
    total_cost: float = 0.0
    total_time: float = 0.0
    success_rate: float = 0.0
    overall_success: bool
    generated_at: datetime = Field(default_factory=datetime.now)
