"""Unit tests for reporters."""

import json
import tempfile
import sqlite3
from pathlib import Path
import pytest

from judge_llm.core.models import EvaluationReport
from judge_llm.reporters.console_reporter import ConsoleReporter
from judge_llm.reporters.json_reporter import JSONReporter
from judge_llm.reporters.html_reporter import HTMLReporter
from judge_llm.reporters.database_reporter import DatabaseReporter


class TestConsoleReporter:
    """Test ConsoleReporter class."""

    def test_console_reporter_creation(self):
        """Test ConsoleReporter instantiation."""
        reporter = ConsoleReporter()
        assert reporter is not None

    def test_console_report_generation(self, sample_evaluation_report, capsys):
        """Test console report generation."""
        reporter = ConsoleReporter()

        # Generate report (should not raise exception)
        reporter.generate_report(sample_evaluation_report)

        # Capture output
        captured = capsys.readouterr()

        # Check that some output was generated
        assert len(captured.out) > 0 or len(captured.err) > 0


class TestJSONReporter:
    """Test JSONReporter class."""

    def test_json_reporter_creation(self, temp_dir):
        """Test JSONReporter instantiation."""
        output_path = temp_dir / "report.json"
        reporter = JSONReporter(str(output_path))
        assert reporter is not None

    def test_json_report_generation(self, sample_evaluation_report, temp_dir):
        """Test JSON report generation."""
        output_path = temp_dir / "report.json"
        reporter = JSONReporter(str(output_path))

        # Generate report
        reporter.generate_report(sample_evaluation_report)

        # Verify file was created
        assert output_path.exists()

        # Verify JSON is valid
        with open(output_path, 'r') as f:
            data = json.load(f)

        assert data is not None

    def test_json_serialization(self, sample_execution_run, temp_dir):
        """Test JSON serialization of complex objects."""
        output_path = temp_dir / "report.json"
        reporter = JSONReporter(str(output_path))

        report = EvaluationReport(
            execution_runs=[sample_execution_run],
            summary={"total": 1},
            overall_success=True
        )

        # Should not raise exception
        reporter.generate_report(report)

        # Verify file was created
        assert output_path.exists()


class TestHTMLReporter:
    """Test HTMLReporter class."""

    def test_html_reporter_creation(self, temp_dir):
        """Test HTMLReporter instantiation."""
        output_path = temp_dir / "report.html"
        reporter = HTMLReporter(str(output_path))
        assert reporter is not None

    def test_html_report_generation(self, sample_evaluation_report, temp_dir):
        """Test HTML report generation."""
        output_path = temp_dir / "report.html"
        reporter = HTMLReporter(str(output_path))

        # Generate report
        reporter.generate_report(sample_evaluation_report)

        # Verify file was created
        assert output_path.exists()

        # Verify HTML content
        with open(output_path, 'r') as f:
            html_content = f.read()

        assert "<html" in html_content or "<!DOCTYPE" in html_content
        assert len(html_content) > 100

    def test_html_template_usage(self, sample_evaluation_report, temp_dir):
        """Test that HTML reporter uses template."""
        output_path = temp_dir / "report.html"
        reporter = HTMLReporter(str(output_path))

        reporter.generate_report(sample_evaluation_report)

        with open(output_path, 'r') as f:
            html_content = f.read()

        # Check for common HTML elements
        assert "html" in html_content.lower()


class TestDatabaseReporter:
    """Test DatabaseReporter class."""

    def test_database_reporter_creation(self, temp_dir):
        """Test DatabaseReporter instantiation."""
        db_path = temp_dir / "test.db"
        reporter = DatabaseReporter(str(db_path))
        assert reporter is not None

        # Database file is created when first report is generated
        # Resolve both paths to handle symlinks (e.g., /var -> /private/var on macOS)
        assert reporter.db_path.resolve() == db_path.resolve()

    def test_database_schema_creation(self, sample_execution_run, temp_dir):
        """Test that database schema is created properly."""
        db_path = temp_dir / "test.db"
        reporter = DatabaseReporter(str(db_path))

        # Generate a report to trigger database initialization
        report = EvaluationReport(
            execution_runs=[sample_execution_run],
            summary={"total": 1},
            overall_success=True
        )
        reporter.generate_report(report)

        # Connect to database and check for tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Verify expected tables exist
        expected_tables = ["reports", "eval_sets", "eval_cases", "execution_runs",
                          "invocations", "evaluator_results"]
        for table in expected_tables:
            assert table in tables

        conn.close()

    def test_database_report_storage(self, sample_execution_run, temp_dir):
        """Test storing report in database."""
        db_path = temp_dir / "test.db"
        reporter = DatabaseReporter(str(db_path))

        report = EvaluationReport(
            execution_runs=[sample_execution_run],
            summary={"total": 1, "passed": 1},
            total_cost=0.001,
            total_time=0.1,
            success_rate=1.0,
            overall_success=True
        )

        # Store report
        reporter.generate_report(report)

        # Verify data was stored
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM reports")
        assert cursor.fetchone()[0] == 1

        cursor.execute("SELECT COUNT(*) FROM execution_runs")
        assert cursor.fetchone()[0] >= 1

        conn.close()

    def test_database_multiple_reports(self, temp_dir):
        """Test storing multiple reports."""
        db_path = temp_dir / "test.db"
        reporter = DatabaseReporter(str(db_path))

        # Create first execution run with unique ID
        from judge_llm.core.models import ExecutionRun, ProviderResult, Invocation, Content, Part, IntermediateData
        exec_run1 = ExecutionRun(
            execution_id="exec_unique_1",
            run_number=1,
            eval_set_id="set_1",
            eval_case_id="test_case_1",
            provider_type="mock",
            provider_result=ProviderResult(
                conversation_history=[
                    Invocation(
                        invocation_id="inv_1",
                        user_content=Content(role="user", parts=[Part(text="Hello")]),
                        final_response=Content(role="model", parts=[Part(text="Hi!")]),
                        intermediate_data=IntermediateData(),
                        creation_timestamp=1234567890.0
                    )
                ],
                cost=0.001,
                time_taken=0.1,
                success=True
            ),
            evaluator_results=[],
            overall_success=True
        )

        # Store first report
        report1 = EvaluationReport(
            execution_runs=[exec_run1],
            summary={},
            overall_success=True
        )
        reporter.generate_report(report1)

        # Create second execution run with different unique ID
        exec_run2 = ExecutionRun(
            execution_id="exec_unique_2",
            run_number=1,
            eval_set_id="set_1",
            eval_case_id="test_case_2",
            provider_type="mock",
            provider_result=ProviderResult(
                conversation_history=[
                    Invocation(
                        invocation_id="inv_2",
                        user_content=Content(role="user", parts=[Part(text="Hello again")]),
                        final_response=Content(role="model", parts=[Part(text="Hi again!")]),
                        intermediate_data=IntermediateData(),
                        creation_timestamp=1234567890.0
                    )
                ],
                cost=0.002,
                time_taken=0.2,
                success=True
            ),
            evaluator_results=[],
            overall_success=True
        )

        # Store second report
        report2 = EvaluationReport(
            execution_runs=[exec_run2],
            summary={},
            overall_success=True
        )
        reporter.generate_report(report2)

        # Verify both stored
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM reports")
        assert cursor.fetchone()[0] == 2

        cursor.execute("SELECT COUNT(*) FROM execution_runs")
        assert cursor.fetchone()[0] == 2

        conn.close()

    def test_database_query_results(self, sample_execution_run, temp_dir):
        """Test querying stored results."""
        db_path = temp_dir / "test.db"
        reporter = DatabaseReporter(str(db_path))

        report = EvaluationReport(
            execution_runs=[sample_execution_run],
            summary={"total": 1},
            overall_success=True
        )

        reporter.generate_report(report)

        # Query the data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM reports")
        result = cursor.fetchone()

        assert result is not None
        assert result[0] > 0

        conn.close()
