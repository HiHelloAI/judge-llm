"""Google ADK provider implementation.

This provider wraps Google's Agent Development Kit (ADK) to work with the
framework's provider-agnostic interface.
"""

from __future__ import annotations

import asyncio
import importlib
import logging
import sys
import threading
import time
import uuid
from typing import Any, Dict, Optional

from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.evaluation.eval_case import get_all_tool_calls
from google.adk.evaluation.evaluation_generator import EvaluationGenerator
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types as genai_types

from judge_llm.core.models import (
    Content,
    EvalCase,
    IntermediateData,
    Invocation,
    Part,
    ProviderResult,
    ToolUse,
)
from judge_llm.providers.base import BaseProvider
from judge_llm.utils.logger import get_logger

logger = get_logger()


class GoogleADKProvider(BaseProvider):
    """Provider implementation for Google ADK."""

    def __init__(
        self,
        agent_id: str,
        agent_config_path: Optional[str] = None,
        agent_metadata: Optional[Dict[str, Any]] = None,
        **provider_metadata,
    ):
        """Initialize ADK provider.

        Args:
            agent_id: Unique identifier for the agent
            agent_config_path: Path to agent configuration directory
            agent_metadata: Agent metadata containing 'module_path' and optional 'agent_name'
            **provider_metadata: Additional provider-specific metadata
        """
        super().__init__(agent_id, agent_config_path, agent_metadata, **provider_metadata)

        # Suppress ADK warnings about default function parameters
        logging.getLogger('google_adk.google.adk.tools._function_parameter_parse_util').setLevel(logging.ERROR)

        self._session_service = InMemorySessionService()
        self._artifact_service = InMemoryArtifactService()
        self._agent = None  # Cached agent instance
        self._agent_lock = threading.Lock()  # Thread-safe agent loading

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """Execute evaluation case using Google ADK agent.

        Args:
            eval_case: The evaluation case to execute

        Returns:
            ProviderResult with conversation history and metadata
        """
        try:
            # Get agent (cached after first load, thread-safe)
            if self._agent is None:
                with self._agent_lock:
                    # Double-check after acquiring lock
                    if self._agent is None:
                        self._agent = self._load_agent()

            # Run ADK inference
            session_id = f"eval_session_{uuid.uuid4()}"
            adk_invocations = self._to_adk_invocations(eval_case.conversation)

            actual_invocations = asyncio.run(
                EvaluationGenerator._generate_inferences_from_root_agent(
                    invocations=adk_invocations,
                    root_agent=self._agent,
                    initial_session=eval_case.session_input,
                    session_id=session_id,
                    session_service=self._session_service,
                    artifact_service=self._artifact_service,
                )
            )

            # Convert results back to framework format
            conversation_history = self._to_framework_invocations(actual_invocations)

            return ProviderResult(
                conversation_history=conversation_history,
                metadata={
                    "provider": "google_adk",
                    "agent_id": self.agent_id,
                    "eval_id": eval_case.eval_id,
                    "session_id": session_id,
                },
                success=True,
            )

        except Exception as e:
            logger.error(f"Inference failed for '{eval_case.eval_id}': {e}", exc_info=True)
            return ProviderResult(
                conversation_history=[],
                metadata={"provider": "google_adk", "agent_id": self.agent_id},
                success=False,
                error=str(e),
            )

    def cleanup(self):
        """Cleanup resources after execution."""
        self._agent = None

    def _load_agent(self) -> LlmAgent:
        """Load agent from module specified in agent_metadata."""
        module_path = self.agent_metadata.get("module_path")
        if not module_path:
            raise ValueError("agent_metadata must contain 'module_path'")

        agent_name = self.agent_metadata.get("agent_name", "root_agent")

        # Add root_path to sys.path if specified
        root_path = self.agent_metadata.get("root_path") or self.agent_config_path
        if root_path and root_path not in sys.path:
            sys.path.insert(0, root_path)

        # Apply module prefix if specified
        if prefix := self.agent_metadata.get("module_prefix"):
            module_path = f"{prefix}.{module_path}"

        # Import and get agent
        try:
            module = importlib.import_module(module_path)
            agent = getattr(module, agent_name, None)

            # Try submodule if direct access fails
            if agent is None:
                submodule_name = self.agent_metadata.get("agent_submodule", "agent")
                if hasattr(module, submodule_name):
                    agent = getattr(getattr(module, submodule_name), agent_name, None)

            if agent is None:
                raise ValueError(f"Agent '{agent_name}' not found in '{module_path}'")

            if not isinstance(agent, LlmAgent):
                raise ValueError(f"Agent must be LlmAgent, got {type(agent).__name__}")

            logger.info(f"Loaded agent '{agent_name}' from '{module_path}'")
            return agent

        except ImportError as e:
            raise ValueError(f"Cannot import '{module_path}': {e}")

    def _to_adk_invocations(self, conversation: list[Invocation]) -> list:
        """Convert framework Invocations to ADK Invocations."""
        from google.adk.evaluation.eval_case import (
            IntermediateData as ADKIntermediateData,
            Invocation as ADKInvocation,
        )

        return [
            ADKInvocation(
                invocation_id=inv.invocation_id,
                user_content=self._to_adk_content(inv.user_content),
                final_response=self._to_adk_content(inv.final_response),
                intermediate_data=ADKIntermediateData(
                    tool_uses=[
                        genai_types.FunctionCall(name=tu.name, args=tu.args)
                        for tu in inv.intermediate_data.tool_uses
                    ],
                    intermediate_responses=inv.intermediate_data.intermediate_responses,
                ),
            )
            for inv in conversation
        ]

    def _to_adk_content(self, content: Content):
        """Convert framework Content to ADK Content."""
        parts = []
        for part in content.parts:
            if part.text:
                parts.append(genai_types.Part(text=part.text))
            elif part.function_call:
                parts.append(genai_types.Part(function_call=part.function_call))
            elif part.function_response:
                parts.append(genai_types.Part(function_response=part.function_response))

        return genai_types.Content(parts=parts, role=content.role or "user")

    def _to_framework_invocations(self, adk_invocations: list) -> list[Invocation]:
        """Convert ADK Invocations to framework Invocations."""
        framework_invocations = []

        for adk_inv in adk_invocations:
            # Extract tool uses
            tool_uses = []
            if adk_inv.intermediate_data:
                tool_calls = get_all_tool_calls(adk_inv.intermediate_data)
                tool_uses = [
                    ToolUse(
                        id=getattr(tc, 'id', str(uuid.uuid4())),
                        name=tc.name,
                        args=dict(tc.args) if tc.args else {}
                    )
                    for tc in tool_calls
                ]

            # Extract intermediate responses (may not exist in all ADK versions)
            intermediate_responses = []
            if adk_inv.intermediate_data and hasattr(adk_inv.intermediate_data, 'intermediate_responses'):
                intermediate_responses = adk_inv.intermediate_data.intermediate_responses or []

            framework_invocations.append(
                Invocation(
                    invocation_id=adk_inv.invocation_id,
                    user_content=self._to_framework_content(adk_inv.user_content, "user"),
                    final_response=self._to_framework_content(adk_inv.final_response, "model"),
                    intermediate_data=IntermediateData(
                        tool_uses=tool_uses,
                        intermediate_responses=intermediate_responses
                    ),
                    creation_timestamp=getattr(adk_inv, 'creation_timestamp', time.time()),
                )
            )

        return framework_invocations

    def _to_framework_content(self, adk_content, default_role: str) -> Content:
        """Convert ADK Content to framework Content."""
        if not adk_content:
            return Content(parts=[], role=default_role)

        parts = []
        if hasattr(adk_content, 'parts') and adk_content.parts:
            for adk_part in adk_content.parts:
                part_dict = {}
                if hasattr(adk_part, 'text') and adk_part.text:
                    part_dict['text'] = adk_part.text
                if hasattr(adk_part, 'function_call') and adk_part.function_call:
                    fc = adk_part.function_call
                    part_dict['function_call'] = {
                        'name': fc.name,
                        'args': dict(fc.args) if fc.args else {}
                    }
                if hasattr(adk_part, 'function_response') and adk_part.function_response:
                    fr = adk_part.function_response
                    part_dict['function_response'] = {
                        'name': getattr(fr, 'name', ''),
                        'response': getattr(fr, 'response', {})
                    }
                if hasattr(adk_part, 'thought') and adk_part.thought:
                    part_dict['thought'] = adk_part.thought

                if part_dict:
                    parts.append(Part(**part_dict))

        return Content(parts=parts, role=getattr(adk_content, 'role', default_role))
