---
sidebar_position: 8
---

# Telemetry & Observability (OpenTelemetry)

Judge LLM includes optional OpenTelemetry (OTEL) instrumentation for deep observability into evaluation runs. Telemetry is **disabled by default** and adds zero overhead when not enabled.

## Overview

When enabled, telemetry provides:

- **Distributed tracing** across the full evaluation lifecycle
- **Span-level detail** for every provider call, evaluator run, and report generation
- **Error tracking** with retry attempts, HTTP status codes, and failure reasons
- **Performance metrics** including latency, token usage, and cost per span
- **Integration with observability platforms** like Arize Phoenix, Jaeger, Grafana Tempo, and Datadog

## Installation

Telemetry dependencies are optional. Install only what you need:

```bash
# Console + OTLP exporters (Jaeger, Grafana Tempo, Datadog, etc.)
pip install judge-llm[telemetry]

# Arize Phoenix (LLM-focused observability)
pip install judge-llm[phoenix]
```

## Enabling Telemetry

Choose any of these methods:

### Method 1: CLI Flag

```bash
# Console exporter (prints spans to stdout)
judge-llm run --config config.yaml --telemetry

# OTLP exporter (sends to Jaeger, Grafana Tempo, etc.)
judge-llm run --config config.yaml --telemetry --telemetry-exporter otlp

# Arize Phoenix
judge-llm run --config config.yaml --telemetry --telemetry-exporter phoenix
```

### Method 2: Environment Variable

```bash
export JUDGE_LLM_TELEMETRY=true
export OTEL_EXPORTER_TYPE=console  # or "otlp" or "phoenix"

judge-llm run --config config.yaml
```

### Method 3: YAML Configuration

```yaml
agent:
  log_level: INFO
  telemetry:
    enabled: true
    exporter: console    # "console", "otlp", or "phoenix"
    service_name: judge-llm  # optional, default: "judge-llm"
    endpoint: http://localhost:4317  # optional, for otlp/phoenix
```

### Method 4: Python API

```python
from judge_llm import evaluate
from judge_llm.utils.telemetry import init_telemetry

# Initialize before calling evaluate
init_telemetry(exporter="phoenix", service_name="my-eval-pipeline")

report = evaluate(config="config.yaml")
```

## Exporters

### Console Exporter

Prints spans to stdout. Useful for debugging and development.

```bash
judge-llm run --config config.yaml --telemetry --telemetry-exporter console
```

No additional setup required.

### OTLP Exporter

Sends spans to any OpenTelemetry-compatible backend via gRPC or HTTP.

```bash
# Set the OTLP endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

judge-llm run --config config.yaml --telemetry --telemetry-exporter otlp
```

Or via YAML:

```yaml
agent:
  telemetry:
    enabled: true
    exporter: otlp
    endpoint: http://localhost:4317
```

**Compatible backends:**
- [Jaeger](https://www.jaegertracing.io/) (port 4317 for gRPC)
- [Grafana Tempo](https://grafana.com/oss/tempo/)
- [Datadog](https://docs.datadoghq.com/tracing/trace_collection/open_standards/otlp_ingest_in_the_agent/)
- Any OTLP-compatible collector

### Arize Phoenix

[Arize Phoenix](https://github.com/Arize-ai/phoenix) is an open-source observability platform built for LLM applications.

#### Setup Phoenix

```bash
# Install Phoenix
pip install arize-phoenix

# Start the Phoenix server
phoenix serve
```

Phoenix will be available at `http://localhost:6006`.

#### Run with Phoenix

```bash
judge-llm run --config config.yaml --telemetry --telemetry-exporter phoenix
```

Or via YAML:

```yaml
agent:
  telemetry:
    enabled: true
    exporter: phoenix
    endpoint: http://localhost:6006  # default
    service_name: my-eval-project    # shows as project name in Phoenix
```

Or via environment variables:

```bash
export JUDGE_LLM_TELEMETRY=true
export OTEL_EXPORTER_TYPE=phoenix
export PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006

judge-llm run --config config.yaml
```

After running, open `http://localhost:6006` to see your traces.

### What Phoenix Shows

With OpenInference semantic conventions (automatically included in `judge-llm[phoenix]`), Phoenix displays:

- **Sessions** — evaluation runs grouped by session ID, showing multi-turn conversation flow
- **Input/Output** — actual user messages and agent response text on each span
- **LLM calls** — model name, token counts (prompt/completion/total), and cost
- **HTTP details** — full request/response payloads and headers on ADK HTTP spans
- **Evaluator results** — pass/fail status, scores, and details
- **Span classification** — spans categorized as CHAIN, LLM, TOOL, or EVALUATOR

## Span Hierarchy

When telemetry is enabled, Judge LLM creates the following span tree for each evaluation:

```
judge_llm.evaluate                                [CHAIN]
├── judge_llm.execute_task                        [CHAIN, session.id, input/output]
│   ├── judge_llm.provider.execute                [LLM, input/output, tokens, model]
│   │   ├── judge_llm.adk_http.create_session     [TOOL, HTTP req/res body]
│   │   └── judge_llm.adk_http.send_and_collect   [LLM, HTTP req/res body, tokens]
│   └── judge_llm.evaluator.evaluate              [EVALUATOR, score, output]
└── judge_llm.reporter.generate                   [per reporter]
```

## Span Attributes

### Root Span: `judge_llm.evaluate`

| Attribute | Type | Description |
|-----------|------|-------------|
| `judge_llm.num_providers` | int | Number of providers configured |
| `judge_llm.num_evaluators` | int | Number of evaluators configured |
| `judge_llm.num_eval_sets` | int | Number of evaluation sets loaded |
| `judge_llm.num_runs` | int | Runs per eval case |
| `judge_llm.parallel` | bool | Whether parallel execution is enabled |
| `judge_llm.total_executions` | int | Total execution runs completed |
| `judge_llm.success_rate` | float | Overall success rate (0.0-1.0) |
| `judge_llm.total_cost` | float | Total cost across all executions |
| `judge_llm.total_time` | float | Total wall-clock time (seconds) |

### Task Span: `judge_llm.execute_task`

| Attribute | Type | Description |
|-----------|------|-------------|
| `judge_llm.eval_case_id` | str | Evaluation case identifier |
| `judge_llm.eval_set_id` | str | Evaluation set identifier |
| `judge_llm.provider_type` | str | Provider type (e.g., "gemini", "adk_http") |
| `judge_llm.run_number` | int | Run number (1-based) |
| `judge_llm.task.success` | bool | Whether the task passed all evaluators |
| `openinference.span.kind` | str | `CHAIN` |
| `session.id` | str | Session ID for Phoenix grouping |
| `input.value` | str | User message(s) from the eval case |
| `output.value` | str | Agent response text |

### Provider Span: `judge_llm.provider.execute`

| Attribute | Type | Description |
|-----------|------|-------------|
| `judge_llm.provider_type` | str | Provider type |
| `judge_llm.agent_id` | str | Agent identifier |
| `judge_llm.provider.success` | bool | Provider execution success |
| `judge_llm.provider.cost` | float | Execution cost |
| `judge_llm.provider.token_usage.total` | int | Total tokens used |
| `openinference.span.kind` | str | `LLM` |
| `session.id` | str | Session ID for Phoenix grouping |
| `input.value` | str | User input text |
| `output.value` | str | Agent response text |
| `llm.model_name` | str | Model name |
| `llm.token_count.prompt` | int | Prompt token count |
| `llm.token_count.completion` | int | Completion token count |
| `llm.token_count.total` | int | Total token count |

**Events recorded on failure:**

| Event | Attributes | Description |
|-------|------------|-------------|
| `provider_error` | `error` | Provider execution error message |

### ADK HTTP Spans

#### `judge_llm.adk_http.create_session`

| Attribute | Type | Description |
|-----------|------|-------------|
| `judge_llm.adk_http.endpoint` | str | Base endpoint URL |
| `judge_llm.adk_http.app_name` | str | Application name |
| `judge_llm.adk_http.user_id` | str | User ID |
| `http.status_code` | int | HTTP response status code |
| `judge_llm.adk_http.session_id` | str | Created session ID |
| `http.request.method` | str | `POST` |
| `http.request.url` | str | Full request URL |
| `http.request.headers` | str | Request headers |
| `http.request.body` | str | Request payload |
| `http.response.body` | str | Response body (truncated to 2KB) |
| `openinference.span.kind` | str | `TOOL` |
| `input.value` | str | `POST {url}` |
| `output.value` | str | Session ID and status |
| `session.id` | str | Created session ID |
| `user.id` | str | User ID |

#### `judge_llm.adk_http.send_and_collect`

| Attribute | Type | Description |
|-----------|------|-------------|
| `judge_llm.adk_http.endpoint` | str | Request endpoint URL |
| `judge_llm.adk_http.session_id` | str | Session ID |
| `http.status_code` | int | HTTP response status code |
| `http.request.method` | str | `POST` |
| `http.request.url` | str | Full request URL |
| `http.request.headers` | str | Request headers (auth excluded) |
| `http.request.body` | str | Request payload (truncated to 4KB, state excluded) |
| `http.response.status_code` | int | Response status code |
| `http.response.headers` | str | Response headers |
| `http.response.body` | str | Response body (truncated to 4KB) |
| `judge_llm.adk_http.event_count` | int | Number of SSE events received |
| `judge_llm.adk_http.content_type` | str | Response content type |
| `judge_llm.adk_http.attempts` | int | Number of attempts (1 = no retries) |
| `openinference.span.kind` | str | `LLM` |
| `session.id` | str | Session ID |
| `input.value` | str | User message text |
| `output.value` | str | Agent response text extracted from events |
| `llm.model_name` | str | Model name |
| `llm.token_count.prompt` | int | Prompt token count |
| `llm.token_count.completion` | int | Completion token count |
| `llm.token_count.total` | int | Total token count |

**Events recorded on retries:**

| Event | Attributes | Description |
|-------|------------|-------------|
| `http_error` | `attempt`, `status_code`, `error` | HTTP status error |
| `request_error` | `attempt`, `error` | Connection/timeout error |
| `unexpected_error` | `attempt`, `error` | Other errors |

### Evaluator Span: `judge_llm.evaluator.evaluate`

| Attribute | Type | Description |
|-----------|------|-------------|
| `judge_llm.evaluator.name` | str | Evaluator name |
| `judge_llm.evaluator.passed` | bool | Whether the evaluator passed |
| `judge_llm.evaluator.score` | float | Evaluator score (-1 if N/A) |
| `openinference.span.kind` | str | `EVALUATOR` |
| `output.value` | str | Evaluator result summary (passed, score, details) |

### Reporter Span: `judge_llm.reporter.generate`

| Attribute | Type | Description |
|-----------|------|-------------|
| `judge_llm.reporter.type` | str | Reporter class name |

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `JUDGE_LLM_TELEMETRY` | Enable telemetry (`true`, `1`, `yes`) | `false` |
| `OTEL_EXPORTER_TYPE` | Exporter type (`console`, `otlp`, `phoenix`) | `console` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | `http://localhost:4317` |
| `PHOENIX_COLLECTOR_ENDPOINT` | Phoenix collector endpoint | `http://localhost:6006` |

## Examples

### Debug a Failing Provider

Enable telemetry to see exactly where a provider call fails:

```bash
JUDGE_LLM_TELEMETRY=true judge-llm run --config config.yaml -l DEBUG
```

The console exporter will show spans with error events, retry attempts, HTTP status codes, and timing for each step.

### Monitor Evaluations in Phoenix

```bash
# Terminal 1: Start Phoenix
pip install arize-phoenix
phoenix serve

# Terminal 2: Run evaluation
pip install judge-llm[phoenix]
judge-llm run --config config.yaml --telemetry --telemetry-exporter phoenix
```

Open `http://localhost:6006` to see:
- **Sessions** grouping related spans by evaluation case
- **Input/Output** showing user messages and agent responses on each span
- **LLM calls** with model name, token counts, and cost
- **HTTP payloads** with full request/response bodies and headers
- **Evaluator results** with scores, pass/fail, and details
- Full trace waterfall with timing for each step
- Error details with retry history

### Send Traces to Jaeger

```bash
# Start Jaeger (Docker)
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest

# Run with OTLP exporter
pip install judge-llm[telemetry]
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
  judge-llm run --config config.yaml --telemetry --telemetry-exporter otlp
```

Open `http://localhost:16686` to view traces in Jaeger UI.

### CI/CD with Telemetry

```yaml
# GitHub Actions
- name: Run evaluation with telemetry
  env:
    JUDGE_LLM_TELEMETRY: true
    OTEL_EXPORTER_TYPE: otlp
    OTEL_EXPORTER_OTLP_ENDPOINT: ${{ secrets.OTEL_ENDPOINT }}
  run: |
    pip install judge-llm[telemetry]
    judge-llm run --config config.yaml
```

## Behavior When Disabled

When telemetry is not enabled (the default):

- **No dependencies required** - `opentelemetry` packages are not imported
- **Zero overhead** - all tracing calls are no-ops that return immediately
- **No side effects** - no spans created, no data sent anywhere
- **Safe to leave in code** - instrumentation points are always present but inactive

## Related Documentation

- [CLI Reference](./cli-reference)
- [Configuration Guide](./configuration)
- [Environment Variables](./environment-variables)
