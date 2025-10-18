"""SQLite Database reporter with complete conversation history tracking"""

import sqlite3
import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from judge_llm.core.models import EvaluationReport, ExecutionRun, EvaluatorResult, Invocation
from judge_llm.reporters.base import BaseReporter
from judge_llm.utils.logger import get_logger


class DatabaseReporter(BaseReporter):
    """Report evaluation results to SQLite database with full conversation tracking"""

    def __init__(self, db_path: str = "./judge_llm_results.db"):
        """Initialize database reporter

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path).expanduser().resolve()
        self.logger = get_logger()
        self.connection = None

    def _init_database(self):
        """Initialize database and create tables if they don't exist"""
        # Create parent directories if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Connect to database
        self.connection = sqlite3.connect(str(self.db_path))
        cursor = self.connection.cursor()

        # Create reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                generated_at TEXT NOT NULL,
                total_cost REAL DEFAULT 0.0,
                total_time REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 0.0,
                overall_success INTEGER NOT NULL,
                summary_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create eval_sets table (for tracking datasets)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eval_sets (
                eval_set_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                creation_timestamp REAL,
                first_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create eval_cases table (for tracking test cases)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eval_cases (
                eval_case_id TEXT PRIMARY KEY,
                eval_set_id TEXT NOT NULL,
                app_name TEXT,
                user_id TEXT,
                user_prompt TEXT,
                system_instruction TEXT,
                creation_timestamp REAL,
                state_json TEXT,
                first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (eval_set_id) REFERENCES eval_sets(eval_set_id)
            )
        """)

        # Create execution_runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_runs (
                execution_id TEXT PRIMARY KEY,
                report_id TEXT NOT NULL,
                run_number INTEGER NOT NULL,
                eval_set_id TEXT NOT NULL,
                eval_case_id TEXT NOT NULL,
                provider_type TEXT NOT NULL,
                provider_model TEXT,
                overall_success INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                cost REAL DEFAULT 0.0,
                time_taken REAL DEFAULT 0.0,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                metadata_json TEXT,
                FOREIGN KEY (report_id) REFERENCES reports(report_id),
                FOREIGN KEY (eval_set_id) REFERENCES eval_sets(eval_set_id),
                FOREIGN KEY (eval_case_id) REFERENCES eval_cases(eval_case_id)
            )
        """)

        # Create invocations table (conversation history)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL,
                invocation_id TEXT NOT NULL,
                invocation_type TEXT NOT NULL,
                sequence_order INTEGER NOT NULL,
                user_message TEXT,
                assistant_message TEXT,
                creation_timestamp REAL,
                user_content_json TEXT,
                final_response_json TEXT,
                intermediate_data_json TEXT,
                FOREIGN KEY (execution_id) REFERENCES execution_runs(execution_id)
            )
        """)

        # Create evaluator_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluator_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL,
                evaluator_name TEXT NOT NULL,
                evaluator_type TEXT NOT NULL,
                success INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                score REAL,
                threshold REAL,
                details_json TEXT,
                error TEXT,
                evaluated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (execution_id) REFERENCES execution_runs(execution_id)
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_runs_report_id
            ON execution_runs(report_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_runs_timestamp
            ON execution_runs(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_runs_provider
            ON execution_runs(provider_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_runs_eval_case
            ON execution_runs(eval_case_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_runs_eval_set
            ON execution_runs(eval_set_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_evaluator_results_execution_id
            ON evaluator_results(execution_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_evaluator_results_evaluator_name
            ON evaluator_results(evaluator_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_evaluator_results_passed
            ON evaluator_results(passed)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invocations_execution_id
            ON invocations(execution_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invocations_type
            ON invocations(invocation_type)
        """)

        self.connection.commit()
        self.logger.debug(f"Database initialized at {self.db_path}")

    def _serialize_json(self, data: Any) -> str:
        """Serialize data to JSON string

        Args:
            data: Data to serialize

        Returns:
            JSON string
        """
        if hasattr(data, 'model_dump'):
            # Pydantic model
            return json.dumps(data.model_dump(mode='json'))
        elif isinstance(data, dict):
            return json.dumps(data)
        else:
            return json.dumps(str(data))

    def _extract_text_from_parts(self, content) -> str:
        """Extract text from content parts

        Args:
            content: Content object with parts

        Returns:
            Concatenated text from all parts
        """
        if not hasattr(content, 'parts'):
            return ""

        text_parts = []
        for part in content.parts:
            if hasattr(part, 'text') and part.text:
                text_parts.append(part.text)
        return "\n".join(text_parts)

    def _insert_report(self, report: EvaluationReport, report_id: str):
        """Insert report summary into reports table

        Args:
            report: EvaluationReport object
            report_id: Unique report identifier
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO reports (
                report_id, generated_at, total_cost, total_time,
                success_rate, overall_success, summary_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            report.generated_at.isoformat(),
            report.total_cost,
            report.total_time,
            report.success_rate,
            1 if report.overall_success else 0,
            self._serialize_json(report.summary)
        ))

    def _insert_or_update_eval_set(self, run: ExecutionRun):
        """Insert or update eval set metadata

        Args:
            run: ExecutionRun object
        """
        if not run.eval_case:
            return

        cursor = self.connection.cursor()

        # Check if eval_set exists
        cursor.execute("SELECT eval_set_id FROM eval_sets WHERE eval_set_id = ?",
                      (run.eval_set_id,))
        exists = cursor.fetchone()

        if not exists:
            # Insert new eval_set (we don't have all metadata in ExecutionRun, so storing minimal info)
            cursor.execute("""
                INSERT INTO eval_sets (eval_set_id, name, description, creation_timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                run.eval_set_id,
                run.eval_set_id,  # Use ID as name if not available
                None,
                run.eval_case.creation_timestamp if run.eval_case else None
            ))

    def _insert_or_update_eval_case(self, run: ExecutionRun):
        """Insert or update eval case metadata

        Args:
            run: ExecutionRun object
        """
        if not run.eval_case:
            return

        cursor = self.connection.cursor()
        eval_case = run.eval_case

        # Check if eval_case exists
        cursor.execute("SELECT eval_case_id FROM eval_cases WHERE eval_case_id = ?",
                      (run.eval_case_id,))
        exists = cursor.fetchone()

        if not exists:
            # Insert new eval_case
            cursor.execute("""
                INSERT INTO eval_cases (
                    eval_case_id, eval_set_id, app_name, user_id,
                    user_prompt, system_instruction, creation_timestamp, state_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run.eval_case_id,
                run.eval_set_id,
                eval_case.session_input.app_name if eval_case.session_input else None,
                eval_case.session_input.user_id if eval_case.session_input else None,
                eval_case.session_input.user_prompt if eval_case.session_input else None,
                eval_case.session_input.system_instruction if eval_case.session_input else None,
                eval_case.creation_timestamp,
                self._serialize_json(eval_case.session_input.state) if eval_case.session_input else None
            ))

    def _insert_execution_run(self, run: ExecutionRun, report_id: str):
        """Insert execution run into execution_runs table

        Args:
            run: ExecutionRun object
            report_id: Associated report ID
        """
        cursor = self.connection.cursor()

        # Extract token usage
        token_usage = run.provider_result.token_usage
        input_tokens = token_usage.get('input_tokens', 0) if token_usage else 0
        output_tokens = token_usage.get('output_tokens', 0) if token_usage else 0
        total_tokens = token_usage.get('total_tokens', input_tokens + output_tokens) if token_usage else 0

        # Extract model from metadata
        model = run.provider_result.metadata.get('model', None) if run.provider_result.metadata else None

        cursor.execute("""
            INSERT INTO execution_runs (
                execution_id, report_id, run_number, eval_set_id, eval_case_id,
                provider_type, provider_model, overall_success, timestamp, cost, time_taken,
                input_tokens, output_tokens, total_tokens, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run.execution_id,
            report_id,
            run.run_number,
            run.eval_set_id,
            run.eval_case_id,
            run.provider_type,
            model,
            1 if run.overall_success else 0,
            run.timestamp.isoformat(),
            run.provider_result.cost,
            run.provider_result.time_taken,
            input_tokens,
            output_tokens,
            total_tokens,
            self._serialize_json(run.provider_result.metadata)
        ))

    def _insert_invocations(self, execution_id: str, conversation_history: list, invocation_type: str = 'actual'):
        """Insert conversation invocations

        Args:
            execution_id: Associated execution ID
            conversation_history: List of Invocation objects
            invocation_type: Type of conversation ('expected' or 'actual')
        """
        cursor = self.connection.cursor()

        for idx, invocation in enumerate(conversation_history):
            user_message = self._extract_text_from_parts(invocation.user_content)
            assistant_message = self._extract_text_from_parts(invocation.final_response)

            cursor.execute("""
                INSERT INTO invocations (
                    execution_id, invocation_id, invocation_type, sequence_order,
                    user_message, assistant_message, creation_timestamp,
                    user_content_json, final_response_json, intermediate_data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id,
                invocation.invocation_id,
                invocation_type,
                idx,
                user_message,
                assistant_message,
                invocation.creation_timestamp,
                self._serialize_json(invocation.user_content),
                self._serialize_json(invocation.final_response),
                self._serialize_json(invocation.intermediate_data)
            ))

    def _insert_evaluator_results(self, execution_id: str, evaluator_results: list):
        """Insert evaluator results into evaluator_results table

        Args:
            execution_id: Associated execution ID
            evaluator_results: List of EvaluatorResult objects
        """
        cursor = self.connection.cursor()
        for result in evaluator_results:
            cursor.execute("""
                INSERT INTO evaluator_results (
                    execution_id, evaluator_name, evaluator_type, success, passed,
                    score, threshold, details_json, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id,
                result.evaluator_name,
                result.evaluator_type,
                1 if result.success else 0,
                1 if result.passed else 0,
                result.score,
                result.threshold,
                self._serialize_json(result.details),
                result.error
            ))

    def generate_report(self, report: EvaluationReport):
        """Generate database report

        Args:
            report: EvaluationReport object
        """
        try:
            # Initialize database if not already done
            if self.connection is None:
                self._init_database()

            # Generate unique report ID
            report_id = f"report_{report.generated_at.isoformat()}"

            self.logger.debug(f"Storing evaluation report to database: {self.db_path}")

            # Insert report summary
            self._insert_report(report, report_id)

            # Insert execution runs and related data
            for run in report.execution_runs:
                # Insert/update eval set and case metadata
                self._insert_or_update_eval_set(run)
                self._insert_or_update_eval_case(run)

                # Insert execution run
                self._insert_execution_run(run, report_id)

                # Insert actual conversation history (provider's response)
                if run.provider_result and run.provider_result.conversation_history:
                    self._insert_invocations(
                        run.execution_id,
                        run.provider_result.conversation_history,
                        invocation_type='actual'
                    )

                # Insert expected conversation history (from eval case)
                if run.eval_case and run.eval_case.conversation:
                    self._insert_invocations(
                        run.execution_id,
                        run.eval_case.conversation,
                        invocation_type='expected'
                    )

                # Insert evaluator results
                self._insert_evaluator_results(run.execution_id, run.evaluator_results)

            # Commit all changes
            self.connection.commit()

            # Get stats for logging
            total_runs = len(report.execution_runs)
            total_evaluations = sum(len(run.evaluator_results) for run in report.execution_runs)
            total_invocations = sum(
                len(run.provider_result.conversation_history) if run.provider_result.conversation_history else 0
                for run in report.execution_runs
            )

            self.logger.info(
                f"💾 Database report saved: {self.db_path} "
                f"({total_runs} runs, {total_evaluations} evaluations, {total_invocations} invocations)"
            )

            # Print helpful message on how to view the dashboard
            print("\n" + "=" * 80)
            print("📊 Results saved to database!")
            print("=" * 80)
            print(f"📁 Database: {self.db_path}")
            print()
            print("🌐 View results in dashboard:")
            print(f"   judge-llm dashboard --db {self.db_path}")
            print()
            print("   Or:")
            print(f"   python -m judge_llm.cli dashboard --db {self.db_path}")
            print()
            print("💡 The dashboard will open in your browser automatically")
            print("=" * 80 + "\n")

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            self.logger.error(f"Error generating database report: {e}")
            raise

    def cleanup(self):
        """Cleanup resources"""
        if self.connection:
            self.connection.close()
            self.connection = None
