"""Report generators for evaluation results"""

from judge_llm.core.registry import register_reporter
from judge_llm.reporters.console_reporter import ConsoleReporter
from judge_llm.reporters.json_reporter import JSONReporter
from judge_llm.reporters.html_reporter import HTMLReporter
from judge_llm.reporters.database_reporter import DatabaseReporter

# Register built-in reporters
register_reporter("console", ConsoleReporter)
register_reporter("json", JSONReporter)
register_reporter("html", HTMLReporter)
register_reporter("database", DatabaseReporter)
