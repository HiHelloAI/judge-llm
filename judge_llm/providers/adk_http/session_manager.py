"""Session manager for ADK HTTP provider."""

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Session:
    """ADK session state."""

    session_id: str
    app_name: str
    user_id: str
    state: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    message_count: int = 0
    is_active: bool = True


class SessionManager:
    """Manages ADK sessions for multi-turn conversations.

    Thread-safe for parallel execution. Tracks session state locally
    while the server maintains the actual conversation history.
    """

    def __init__(self):
        """Initialize session manager."""
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()

    def create_session(
        self,
        app_name: str,
        user_id: str,
        initial_state: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """Create a new session.

        Args:
            app_name: Application name for the session
            user_id: User ID for the session
            initial_state: Optional initial state dict
            session_id: Optional fixed session ID (auto-generated if not provided)

        Returns:
            Session ID string
        """
        with self._lock:
            session_id = session_id or f"eval_session_{uuid.uuid4().hex[:12]}"

            self._sessions[session_id] = Session(
                session_id=session_id,
                app_name=app_name,
                user_id=user_id,
                state=initial_state.copy() if initial_state else {},
            )

            return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID.

        Args:
            session_id: Session ID to look up

        Returns:
            Session object or None if not found
        """
        with self._lock:
            return self._sessions.get(session_id)

    def update_state(self, session_id: str, state_delta: Dict[str, Any]) -> None:
        """Update session state with delta from ADK response.

        Args:
            session_id: Session ID to update
            state_delta: State changes to apply
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.state.update(state_delta)
                session.last_activity = time.time()
                session.message_count += 1

    def increment_message_count(self, session_id: str) -> None:
        """Increment the message count for a session.

        Args:
            session_id: Session ID to update
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.message_count += 1
                session.last_activity = time.time()

    def close_session(self, session_id: str) -> None:
        """Mark session as inactive.

        Args:
            session_id: Session ID to close
        """
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].is_active = False

    def delete_session(self, session_id: str) -> None:
        """Delete a session completely.

        Args:
            session_id: Session ID to delete
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

    def cleanup_inactive(self, max_age_seconds: int = 3600) -> int:
        """Remove inactive sessions older than max_age_seconds.

        Args:
            max_age_seconds: Maximum age in seconds for inactive sessions

        Returns:
            Number of sessions removed
        """
        with self._lock:
            now = time.time()
            to_remove = [
                sid
                for sid, session in self._sessions.items()
                if not session.is_active
                and (now - session.last_activity) > max_age_seconds
            ]

            for sid in to_remove:
                del self._sessions[sid]

            return len(to_remove)

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs.

        Returns:
            List of active session IDs
        """
        with self._lock:
            return [
                sid for sid, session in self._sessions.items() if session.is_active
            ]

    def get_session_count(self) -> int:
        """Get total number of sessions.

        Returns:
            Number of sessions
        """
        with self._lock:
            return len(self._sessions)
