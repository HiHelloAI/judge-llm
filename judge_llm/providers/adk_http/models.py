"""Pydantic models for ADK SSE event data.

These models represent the structure of events received from ADK HTTP endpoints
via Server-Sent Events (SSE) streaming.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ADKFunctionCall(BaseModel):
    """ADK function call structure within a content part."""

    id: str
    name: str
    args: Dict[str, Any] = Field(default_factory=dict)


class ADKFunctionResponse(BaseModel):
    """ADK function response structure within a content part."""

    id: str
    name: str
    response: Dict[str, Any] = Field(default_factory=dict)


class ADKPart(BaseModel):
    """ADK content part - can contain text, function calls, or function responses."""

    text: Optional[str] = None
    functionCall: Optional[ADKFunctionCall] = None
    functionResponse: Optional[ADKFunctionResponse] = None
    thought: Optional[str] = None


class ADKContent(BaseModel):
    """ADK content structure containing parts and role."""

    parts: List[ADKPart] = Field(default_factory=list)
    role: str = "model"


class ADKUsageMetadata(BaseModel):
    """Token usage metadata from ADK response."""

    candidatesTokenCount: int = 0
    candidatesTokensDetails: Optional[List[Dict[str, Any]]] = None
    promptTokenCount: int = 0
    promptTokensDetails: Optional[List[Dict[str, Any]]] = None
    totalTokenCount: int = 0


class ADKActions(BaseModel):
    """ADK actions structure containing state changes and agent transfers."""

    stateDelta: Dict[str, Any] = Field(default_factory=dict)
    artifactDelta: Dict[str, Any] = Field(default_factory=dict)
    transferToAgent: Optional[str] = None
    requestedAuthConfigs: Dict[str, Any] = Field(default_factory=dict)
    requestedToolConfirmations: Dict[str, Any] = Field(default_factory=dict)


class ADKEvent(BaseModel):
    """Full ADK SSE event structure.

    Represents a single event from the ADK HTTP endpoint SSE stream.

    Example event data:
    ```json
    {
        "modelVersion": "gemini-2.0-flash",
        "content": {"parts": [{"text": "Hello!"}], "role": "model"},
        "finishReason": "STOP",
        "usageMetadata": {"candidatesTokenCount": 10, "promptTokenCount": 5, "totalTokenCount": 15},
        "invocationId": "e-xxx-xxx",
        "author": "TravelCoordinator",
        "actions": {"stateDelta": {}, "transferToAgent": "SearchAgent"},
        "timestamp": 1704067200.123
    }
    ```
    """

    modelVersion: Optional[str] = None
    content: Optional[ADKContent] = None
    finishReason: Optional[str] = None
    usageMetadata: Optional[ADKUsageMetadata] = None
    avgLogprobs: Optional[float] = None
    invocationId: Optional[str] = None
    author: Optional[str] = None
    actions: Optional[ADKActions] = None
    longRunningToolIds: List[str] = Field(default_factory=list)
    id: Optional[str] = None
    timestamp: Optional[float] = None

    # Error handling
    error: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}  # Allow additional fields for forward compatibility
