"""SSE (Server-Sent Events) stream parser for ADK HTTP responses."""

import json
from typing import Any, AsyncIterator, Dict, Iterator, Optional

from judge_llm.providers.adk_http.models import ADKEvent
from judge_llm.utils.logger import get_logger

logger = get_logger()


class SSEParser:
    """Parser for Server-Sent Events streams from ADK HTTP endpoints.

    Handles the SSE format:
        data: {"json": "payload"}

        data: {"another": "event"}

    Each event is separated by double newlines, and data lines are prefixed with "data: ".
    """

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single SSE data line.

        Args:
            line: Raw line from SSE stream

        Returns:
            Parsed JSON dict if line contains data, None otherwise
        """
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith(":"):
            return None

        # Extract data from "data: " prefixed lines
        if line.startswith("data: "):
            data_str = line[6:]  # Remove "data: " prefix
            if data_str:
                try:
                    return json.loads(data_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse SSE JSON data: {e}")
                    return None

        return None

    def parse_stream(self, response) -> Iterator[ADKEvent]:
        """Parse SSE stream from HTTP response (sync version).

        Args:
            response: HTTP response object with iter_bytes() or iter_lines() method

        Yields:
            ADKEvent objects parsed from the stream
        """
        buffer = ""

        # Handle both httpx and requests-style responses
        if hasattr(response, "iter_bytes"):
            iterator = response.iter_bytes()
        elif hasattr(response, "iter_content"):
            iterator = response.iter_content(decode_unicode=True)
        else:
            raise ValueError("Response object must have iter_bytes() or iter_content() method")

        for chunk in iterator:
            if isinstance(chunk, bytes):
                chunk = chunk.decode("utf-8")
            buffer += chunk

            # Process complete lines
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                parsed = self.parse_line(line)

                if parsed is not None:
                    try:
                        event = ADKEvent.model_validate(parsed)
                        yield event
                    except Exception as e:
                        logger.warning(f"Failed to validate ADK event: {e}")
                        continue

    async def parse_stream_async(self, response) -> AsyncIterator[ADKEvent]:
        """Parse SSE stream from HTTP response (async version).

        Args:
            response: Async HTTP response object with aiter_bytes() method

        Yields:
            ADKEvent objects parsed from the stream
        """
        buffer = ""

        async for chunk in response.aiter_bytes():
            if isinstance(chunk, bytes):
                chunk = chunk.decode("utf-8")
            buffer += chunk

            # Process complete lines
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                parsed = self.parse_line(line)

                if parsed is not None:
                    try:
                        event = ADKEvent.model_validate(parsed)
                        yield event
                    except Exception as e:
                        logger.warning(f"Failed to validate ADK event: {e}")
                        continue

    def parse_string(self, data: str) -> Iterator[ADKEvent]:
        """Parse SSE data from a string (useful for testing).

        Args:
            data: Raw SSE string with multiple events

        Yields:
            ADKEvent objects parsed from the string
        """
        for line in data.split("\n"):
            parsed = self.parse_line(line)
            if parsed is not None:
                try:
                    event = ADKEvent.model_validate(parsed)
                    yield event
                except Exception as e:
                    logger.warning(f"Failed to validate ADK event: {e}")
                    continue
