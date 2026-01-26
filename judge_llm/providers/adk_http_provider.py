"""ADK HTTP Provider for remote ADK endpoint integration.

This provider connects to remote ADK HTTP endpoints that stream responses
via Server-Sent Events (SSE), parses the event data, and extracts
evaluation metrics including tool usage, token counts, and costs.
"""

import base64
import os
import time
import uuid
from typing import Any, Dict, List, Optional

from judge_llm.core.models import (
    Content,
    EvalCase,
    Invocation,
    Part,
    ProviderResult,
)
from judge_llm.providers.base import BaseProvider
from judge_llm.providers.adk_http.models import ADKEvent
from judge_llm.providers.adk_http.sse_parser import SSEParser
from judge_llm.providers.adk_http.event_mapper import EventMapper
from judge_llm.providers.adk_http.session_manager import SessionManager
from judge_llm.providers.adk_http.pricing import PricingCalculator
from judge_llm.utils.logger import get_logger

logger = get_logger()

# Prefix for evaluation session IDs to distinguish them from regular sessions
EVAL_SESSION_ID_PREFIX = '___eval___session___'


class ADKHTTPProvider(BaseProvider):
    """Provider for remote ADK HTTP endpoints with SSE streaming.

    This provider connects to ADK HTTP endpoints, sends user messages,
    receives streaming SSE responses, and maps the events to the
    framework's evaluation models.

    Configuration options:
        - endpoint_url: Base URL for ADK HTTP endpoint (required)
        - auth_type: Authentication type (bearer, api_key, basic, none)
        - api_key: API key for authentication
        - auth_header: Custom auth header name (for api_key type)
        - username/password: For basic auth
        - timeout: Request timeout in seconds
        - model: Model name for cost calculation
        - retry_attempts: Number of retry attempts
        - retry_delay: Delay between retries
    """

    def __init__(
        self,
        agent_id: str,
        agent_config_path: Optional[str] = None,
        agent_metadata: Optional[Dict[str, Any]] = None,
        **provider_metadata,
    ):
        """Initialize ADK HTTP provider.

        Args:
            agent_id: Unique identifier for the agent
            agent_config_path: Not used for HTTP provider
            agent_metadata: Agent metadata (optional)
            **provider_metadata: Provider configuration including:
                - endpoint_url: Base URL for ADK endpoint (required)
                - auth_type: "bearer" | "api_key" | "basic" | "none"
                - api_key: API key (or set ADK_API_KEY env var)
                - auth_header: Custom header name for api_key type
                - username: For basic auth
                - password: For basic auth
                - timeout: Request timeout in seconds (default: 60)
                - model: Model name for cost calculation (default: "gemini-2.0-flash")
                - user_id: User ID for sessions (default: "eval_user")
                - app_name: App name for sessions (default: "judge-llm")
                - retry_attempts: Number of retries (default: 3)
                - retry_delay: Base delay between retries (default: 1)
                - verify_ssl: SSL verification (default: True)
        """
        super().__init__(agent_id, agent_config_path, agent_metadata, **provider_metadata)

        # Required configuration
        self.endpoint_url = provider_metadata.get("endpoint_url")
        if not self.endpoint_url:
            raise ValueError("endpoint_url is required for ADKHTTPProvider")

        # Authentication configuration
        self.auth_type = provider_metadata.get("auth_type", "bearer")
        self.api_key = provider_metadata.get("api_key") or os.environ.get("ADK_API_KEY")
        self.auth_header = provider_metadata.get("auth_header", "X-API-Key")
        self.username = provider_metadata.get("username")
        self.password = provider_metadata.get("password")

        # Request configuration
        self.timeout = provider_metadata.get("timeout", 60)
        self.verify_ssl = provider_metadata.get("verify_ssl", True)
        self.retry_attempts = provider_metadata.get("retry_attempts", 3)
        self.retry_delay = provider_metadata.get("retry_delay", 1)

        # Session configuration
        self.user_id = provider_metadata.get("user_id", "eval_user")
        self.app_name = provider_metadata.get("app_name", "judge-llm")

        # Model for cost calculation
        self.model = provider_metadata.get("model", "gemini-2.0-flash")

        # Custom pricing (optional)
        custom_pricing = provider_metadata.get("custom_pricing")

        # Initialize components
        self._session_manager = SessionManager()
        self._sse_parser = SSEParser()
        self._event_mapper = EventMapper()
        self._pricing = PricingCalculator(custom_pricing=custom_pricing)

        # HTTP client (lazy initialization)
        self._client = None

        # Server base URL (derived from endpoint_url)
        # e.g., http://127.0.0.1:8000/run -> http://127.0.0.1:8000
        self.base_url = self.endpoint_url.rsplit("/", 1)[0]

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """Execute evaluation case against ADK HTTP endpoint.

        Args:
            eval_case: The evaluation case to execute

        Returns:
            ProviderResult with conversation history, cost, tokens, etc.
        """
        start_time = time.time()
        session_id = None

        try:
            # Import httpx here to make it an optional dependency
            import httpx

            # Determine app and user
            app_name = eval_case.session_input.app_name or self.app_name
            user_id = eval_case.session_input.user_id or self.user_id

            # Create session on the ADK server
            server_session_id = self._create_server_session(
                app_name=app_name,
                user_id=user_id,
                initial_state=eval_case.session_input.state,
            )

            # Also track locally
            session_id = self._session_manager.create_session(
                app_name=app_name,
                user_id=user_id,
                initial_state=eval_case.session_input.state,
                session_id=server_session_id,  # Use server's session ID
            )

            conversation_history: List[Invocation] = []
            total_tokens = {"prompt": 0, "completion": 0, "total": 0}
            all_events: List[ADKEvent] = []

            # Execute each turn in the conversation
            for turn_idx, invocation in enumerate(eval_case.conversation):
                user_message = self._extract_user_message(invocation)

                logger.debug(
                    f"Executing turn {turn_idx + 1}/{len(eval_case.conversation)} "
                    f"for eval_case {eval_case.eval_id}"
                )

                # Send request and collect SSE events
                events = self._send_and_collect(
                    session_id=session_id,
                    message=user_message,
                    system_instruction=eval_case.session_input.system_instruction,
                )

                all_events.extend(events)

                # Map events to framework invocation
                result_invocation = self._event_mapper.map_to_invocation(
                    events=events,
                    original_invocation=invocation,
                )

                conversation_history.append(result_invocation)

                # Aggregate token usage
                turn_tokens = self._event_mapper.aggregate_token_usage(events)
                total_tokens["prompt"] += turn_tokens["prompt_tokens"]
                total_tokens["completion"] += turn_tokens["completion_tokens"]
                total_tokens["total"] += turn_tokens["total_tokens"]

                # Update session message count
                self._session_manager.increment_message_count(session_id)

            # Calculate cost
            cost = self._pricing.calculate_cost(
                model=self.model,
                prompt_tokens=total_tokens["prompt"],
                completion_tokens=total_tokens["completion"],
            )

            # Get model version from events
            model_version = self._event_mapper.get_model_version(all_events)

            return ProviderResult(
                conversation_history=conversation_history,
                cost=cost,
                time_taken=time.time() - start_time,
                token_usage={
                    "prompt_tokens": total_tokens["prompt"],
                    "completion_tokens": total_tokens["completion"],
                    "total_tokens": total_tokens["total"],
                },
                metadata={
                    "provider": "adk_http",
                    "agent_id": self.agent_id,
                    "model": model_version or self.model,
                    "session_id": session_id,
                    "eval_id": eval_case.eval_id,
                    "endpoint": self.endpoint_url,
                    "event_count": len(all_events),
                    "agent_chain": self._event_mapper.get_agent_chain(all_events),
                },
                success=True,
            )

        except ImportError:
            logger.error("httpx is required for ADKHTTPProvider. Install with: pip install httpx")
            return ProviderResult(
                conversation_history=[],
                time_taken=time.time() - start_time,
                metadata={"provider": "adk_http", "error": "httpx not installed"},
                success=False,
                error="httpx is required. Install with: pip install httpx",
            )

        except Exception as e:
            logger.error(f"ADK HTTP execution failed: {e}", exc_info=True)
            return ProviderResult(
                conversation_history=[],
                time_taken=time.time() - start_time,
                metadata={
                    "provider": "adk_http",
                    "agent_id": self.agent_id,
                    "error": str(e),
                },
                success=False,
                error=str(e),
            )

        finally:
            if session_id:
                self._session_manager.close_session(session_id)

    def cleanup(self):
        """Cleanup HTTP client and session resources."""
        if self._client is not None:
            self._client.close()
            self._client = None

        # Cleanup inactive sessions
        self._session_manager.cleanup_inactive()

    def _extract_user_message(self, invocation: Invocation) -> str:
        """Extract user message text from invocation.

        Args:
            invocation: The invocation containing user content

        Returns:
            User message as string
        """
        text_parts = []
        for part in invocation.user_content.parts:
            if part.text:
                text_parts.append(part.text)

        return " ".join(text_parts)

    def _create_server_session(
        self,
        app_name: str,
        user_id: str,
        initial_state: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a session on the ADK server.

        Args:
            app_name: Application name
            user_id: User ID
            initial_state: Optional initial state

        Returns:
            Session ID with eval prefix
        """
        import httpx

        # Generate session ID with eval prefix
        session_id = f'{EVAL_SESSION_ID_PREFIX}{str(uuid.uuid4())}'

        url = f"{self.base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"

        headers = {"Content-Type": "application/json"}
        headers.update(self._build_auth_headers())

        payload = {}
        if initial_state:
            payload["state"] = initial_state

        with httpx.Client(
            verify=self.verify_ssl,
            timeout=httpx.Timeout(self.timeout),
        ) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            return session_id

    def _build_auth_headers(self) -> Dict[str, str]:
        """Build authentication headers based on auth_type.

        Returns:
            Dict of authentication headers
        """
        headers: Dict[str, str] = {}

        if self.auth_type == "bearer":
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

        elif self.auth_type == "api_key":
            if self.api_key:
                headers[self.auth_header] = self.api_key

        elif self.auth_type == "basic":
            if self.username and self.password:
                credentials = f"{self.username}:{self.password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded}"

        # auth_type == "none" - no auth headers

        return headers

    def _send_and_collect(
        self,
        session_id: str,
        message: str,
        system_instruction: Optional[str] = None,
    ) -> List[ADKEvent]:
        """Send message to ADK endpoint and collect all events.

        Supports both SSE streaming and JSON array response formats.

        Args:
            session_id: Current session ID
            message: User message text
            system_instruction: Optional system instruction

        Returns:
            List of parsed ADK events
        """
        import httpx

        # Get session info
        session = self._session_manager.get_session(session_id)

        # Build request payload
        payload: Dict[str, Any] = {
            "app_name": session.app_name if session else self.app_name,
            "user_id": session.user_id if session else self.user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}],
            },
        }

        if system_instruction:
            payload["system_instruction"] = system_instruction

        # Include session state if exists
        if session and session.state:
            payload["state"] = session.state

        # Build headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        headers.update(self._build_auth_headers())

        events: List[ADKEvent] = []
        last_error: Optional[Exception] = None

        # Retry logic with exponential backoff
        for attempt in range(self.retry_attempts):
            try:
                with httpx.Client(
                    verify=self.verify_ssl,
                    timeout=httpx.Timeout(self.timeout),
                ) as client:
                    # First try non-streaming request (JSON array response)
                    response = client.post(
                        self.endpoint_url,
                        json=payload,
                        headers=headers,
                    )
                    response.raise_for_status()

                    content_type = response.headers.get("content-type", "")

                    if "text/event-stream" in content_type:
                        # Handle SSE streaming response
                        for event in self._sse_parser.parse_string(response.text):
                            events.append(event)
                            if event.actions and event.actions.stateDelta:
                                self._session_manager.update_state(
                                    session_id,
                                    event.actions.stateDelta,
                                )
                    else:
                        # Handle JSON array response
                        data = response.json()
                        if isinstance(data, list):
                            for item in data:
                                try:
                                    event = ADKEvent.model_validate(item)
                                    events.append(event)
                                    if event.actions and event.actions.stateDelta:
                                        self._session_manager.update_state(
                                            session_id,
                                            event.actions.stateDelta,
                                        )
                                except Exception as e:
                                    logger.warning(f"Failed to parse event: {e}")
                        elif isinstance(data, dict):
                            # Single event response
                            try:
                                event = ADKEvent.model_validate(data)
                                events.append(event)
                                if event.actions and event.actions.stateDelta:
                                    self._session_manager.update_state(
                                        session_id,
                                        event.actions.stateDelta,
                                    )
                            except Exception as e:
                                logger.warning(f"Failed to parse event: {e}")

                    return events

            except httpx.HTTPStatusError as e:
                last_error = e
                try:
                    error_text = e.response.text[:200]
                except Exception:
                    error_text = str(e)
                logger.warning(
                    f"HTTP error on attempt {attempt + 1}/{self.retry_attempts}: "
                    f"{e.response.status_code} - {error_text}"
                )

            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    f"Request error on attempt {attempt + 1}/{self.retry_attempts}: {e}"
                )

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Unexpected error on attempt {attempt + 1}/{self.retry_attempts}: {e}"
                )

            # Exponential backoff before retry
            if attempt < self.retry_attempts - 1:
                delay = self.retry_delay * (2**attempt)
                logger.debug(f"Retrying in {delay}s...")
                time.sleep(delay)

        raise RuntimeError(
            f"Failed after {self.retry_attempts} attempts: {last_error}"
        )

    async def execute_async(self, eval_case: EvalCase) -> ProviderResult:
        """Execute evaluation case asynchronously.

        Args:
            eval_case: The evaluation case to execute

        Returns:
            ProviderResult with conversation history, cost, tokens, etc.
        """
        import httpx

        start_time = time.time()
        session_id = None

        try:
            session_id = self._session_manager.create_session(
                app_name=eval_case.session_input.app_name or self.app_name,
                user_id=eval_case.session_input.user_id or self.user_id,
                initial_state=eval_case.session_input.state,
            )

            conversation_history: List[Invocation] = []
            total_tokens = {"prompt": 0, "completion": 0, "total": 0}
            all_events: List[ADKEvent] = []

            async with httpx.AsyncClient(
                verify=self.verify_ssl,
                timeout=httpx.Timeout(self.timeout),
            ) as client:
                for invocation in eval_case.conversation:
                    user_message = self._extract_user_message(invocation)
                    events = await self._send_and_collect_async(
                        client=client,
                        session_id=session_id,
                        message=user_message,
                        system_instruction=eval_case.session_input.system_instruction,
                    )

                    all_events.extend(events)

                    result_invocation = self._event_mapper.map_to_invocation(
                        events=events,
                        original_invocation=invocation,
                    )
                    conversation_history.append(result_invocation)

                    turn_tokens = self._event_mapper.aggregate_token_usage(events)
                    total_tokens["prompt"] += turn_tokens["prompt_tokens"]
                    total_tokens["completion"] += turn_tokens["completion_tokens"]
                    total_tokens["total"] += turn_tokens["total_tokens"]

            cost = self._pricing.calculate_cost(
                model=self.model,
                prompt_tokens=total_tokens["prompt"],
                completion_tokens=total_tokens["completion"],
            )

            return ProviderResult(
                conversation_history=conversation_history,
                cost=cost,
                time_taken=time.time() - start_time,
                token_usage={
                    "prompt_tokens": total_tokens["prompt"],
                    "completion_tokens": total_tokens["completion"],
                    "total_tokens": total_tokens["total"],
                },
                metadata={
                    "provider": "adk_http",
                    "agent_id": self.agent_id,
                    "model": self._event_mapper.get_model_version(all_events) or self.model,
                    "session_id": session_id,
                    "eval_id": eval_case.eval_id,
                    "event_count": len(all_events),
                },
                success=True,
            )

        except Exception as e:
            logger.error(f"Async ADK HTTP execution failed: {e}", exc_info=True)
            return ProviderResult(
                conversation_history=[],
                time_taken=time.time() - start_time,
                metadata={"provider": "adk_http", "error": str(e)},
                success=False,
                error=str(e),
            )

        finally:
            if session_id:
                self._session_manager.close_session(session_id)

    async def _send_and_collect_async(
        self,
        client,
        session_id: str,
        message: str,
        system_instruction: Optional[str] = None,
    ) -> List[ADKEvent]:
        """Async version of send and collect.

        Args:
            client: httpx.AsyncClient instance
            session_id: Current session ID
            message: User message text
            system_instruction: Optional system instruction

        Returns:
            List of parsed ADK events
        """
        session = self._session_manager.get_session(session_id)

        payload: Dict[str, Any] = {
            "app_name": session.app_name if session else self.app_name,
            "user_id": session.user_id if session else self.user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}],
            },
        }

        if system_instruction:
            payload["system_instruction"] = system_instruction

        if session and session.state:
            payload["state"] = session.state

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        headers.update(self._build_auth_headers())

        events: List[ADKEvent] = []

        async with client.stream(
            "POST",
            self.endpoint_url,
            json=payload,
            headers=headers,
        ) as response:
            response.raise_for_status()

            async for event in self._sse_parser.parse_stream_async(response):
                events.append(event)

                if event.actions and event.actions.stateDelta:
                    self._session_manager.update_state(
                        session_id,
                        event.actions.stateDelta,
                    )

        return events
