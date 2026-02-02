"""Optional OpenTelemetry instrumentation for Judge LLM framework.

Disabled by default. Enable via:
  - Environment variable: JUDGE_LLM_TELEMETRY=true
  - CLI flag: --telemetry
  - YAML config: agent.telemetry.enabled: true

Install dependencies:
  pip install judge-llm[telemetry]       # console + OTLP exporters
  pip install judge-llm[phoenix]         # Arize Phoenix support
"""

import os
import logging
from contextlib import contextmanager
from typing import Any, Dict, Optional

logger = logging.getLogger("judge_llm")

_ENABLED = False
_tracer = None
_provider = None

# Check if opentelemetry is available
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import StatusCode

    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False


def is_telemetry_available() -> bool:
    """Check if OpenTelemetry packages are installed."""
    return _OTEL_AVAILABLE


def is_telemetry_enabled() -> bool:
    """Check if telemetry is currently enabled."""
    return _ENABLED


def init_telemetry(
    service_name: str = "judge-llm",
    exporter: str = "console",
    endpoint: Optional[str] = None,
) -> bool:
    """Initialize OpenTelemetry tracing.

    Args:
        service_name: Service name for traces
        exporter: Exporter type - "console", "otlp", or "phoenix"
        endpoint: OTLP/Phoenix endpoint URL (uses OTEL_EXPORTER_OTLP_ENDPOINT env var if not set)

    Returns:
        True if initialization succeeded, False otherwise
    """
    global _ENABLED, _tracer, _provider

    if not _OTEL_AVAILABLE:
        logger.warning(
            "OpenTelemetry not installed. Install with: pip install judge-llm[telemetry]"
        )
        return False

    try:
        if exporter == "phoenix":
            return _init_phoenix(service_name, endpoint)

        resource = Resource.create({"service.name": service_name})
        _provider = TracerProvider(resource=resource)

        if exporter == "otlp":
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                    OTLPSpanExporter,
                )
            except ImportError:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                    OTLPSpanExporter,
                )

            otlp_endpoint = endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
            if otlp_endpoint:
                span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            else:
                span_exporter = OTLPSpanExporter()
        else:
            span_exporter = ConsoleSpanExporter()

        _provider.add_span_processor(BatchSpanProcessor(span_exporter))
        trace.set_tracer_provider(_provider)
        _tracer = trace.get_tracer("judge_llm")
        _ENABLED = True

        logger.info(f"Telemetry enabled (exporter={exporter})")
        return True

    except Exception as e:
        logger.warning(f"Failed to initialize telemetry: {e}")
        return False


def _init_phoenix(service_name: str, endpoint: Optional[str] = None) -> bool:
    """Initialize telemetry using Arize Phoenix.

    Phoenix uses its own `register()` which sets up a TracerProvider
    that sends spans to a Phoenix server.

    Args:
        service_name: Project/service name
        endpoint: Phoenix endpoint (defaults to PHOENIX_COLLECTOR_ENDPOINT or http://localhost:6006)

    Returns:
        True if initialization succeeded
    """
    global _ENABLED, _tracer, _provider

    try:
        from phoenix.otel import register
    except ImportError:
        logger.warning(
            "arize-phoenix-otel not installed. Install with: pip install judge-llm[phoenix]"
        )
        return False

    try:
        phoenix_endpoint = (
            endpoint
            or os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")
            or "http://localhost:6006"
        )

        _provider = register(
            project_name=service_name,
            endpoint=phoenix_endpoint,
        )

        from opentelemetry import trace
        _tracer = trace.get_tracer("judge_llm")
        _ENABLED = True

        logger.info(f"Telemetry enabled (exporter=phoenix, endpoint={phoenix_endpoint})")
        return True

    except Exception as e:
        logger.warning(f"Failed to initialize Phoenix telemetry: {e}")
        return False


def shutdown_telemetry():
    """Flush and shut down the tracer provider."""
    global _ENABLED, _tracer, _provider
    if _provider is not None:
        try:
            _provider.force_flush()
            _provider.shutdown()
        except Exception:
            pass
    _ENABLED = False
    _tracer = None
    _provider = None


def get_tracer():
    """Get the OTEL tracer instance (or None if disabled)."""
    return _tracer


@contextmanager
def trace_span(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Create a traced span. No-op if telemetry is disabled.

    Args:
        name: Span name
        attributes: Optional span attributes

    Yields:
        The span object (or None if disabled)
    """
    if not _ENABLED or _tracer is None:
        yield None
        return

    with _tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                if value is not None:
                    # OTEL only accepts str, bool, int, float, or sequences thereof
                    if isinstance(value, (str, bool, int, float)):
                        span.set_attribute(key, value)
                    else:
                        span.set_attribute(key, str(value))
        try:
            yield span
        except Exception as e:
            span.set_status(StatusCode.ERROR, str(e))
            span.record_exception(e)
            raise


def record_span_event(span, name: str, attributes: Optional[Dict[str, Any]] = None):
    """Record an event on a span if telemetry is enabled."""
    if span is None or not _ENABLED:
        return
    clean_attrs = {}
    if attributes:
        for k, v in attributes.items():
            if v is not None:
                clean_attrs[k] = str(v) if not isinstance(v, (str, bool, int, float)) else v
    span.add_event(name, attributes=clean_attrs)


def set_span_attributes(span, attributes: Dict[str, Any]):
    """Set attributes on a span if telemetry is enabled."""
    if span is None or not _ENABLED:
        return
    for key, value in attributes.items():
        if value is not None:
            if isinstance(value, (str, bool, int, float)):
                span.set_attribute(key, value)
            else:
                span.set_attribute(key, str(value))


def maybe_init_from_config(agent_config: Dict[str, Any]):
    """Initialize telemetry from agent config if enabled.

    Checks agent_config["telemetry"]["enabled"] and env var JUDGE_LLM_TELEMETRY.

    Args:
        agent_config: The agent configuration dictionary
    """
    if _ENABLED:
        return

    telemetry_config = agent_config.get("telemetry", {})
    enabled = telemetry_config.get("enabled", False)

    # Also check env var
    if not enabled:
        enabled = os.environ.get("JUDGE_LLM_TELEMETRY", "").lower() in ("true", "1", "yes")

    if not enabled:
        return

    exporter = telemetry_config.get(
        "exporter", os.environ.get("OTEL_EXPORTER_TYPE", "console")
    )
    service_name = telemetry_config.get("service_name", "judge-llm")
    endpoint = telemetry_config.get("endpoint")

    init_telemetry(service_name=service_name, exporter=exporter, endpoint=endpoint)
