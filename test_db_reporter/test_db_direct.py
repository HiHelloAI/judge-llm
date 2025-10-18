#!/usr/bin/env python3
"""Direct test of database reporter without requiring API calls"""

import sys
from pathlib import Path
from datetime import datetime
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from judge_llm.core.models import (
    EvaluationReport,
    ExecutionRun,
    ProviderResult,
    EvaluatorResult,
    EvalCase,
    SessionInput,
    Invocation,
    Content,
    Part,
    IntermediateData
)
from judge_llm.reporters.database_reporter import DatabaseReporter

def create_sample_report() -> EvaluationReport:
    """Create a sample evaluation report for testing"""

    # Create sample invocation
    invocation = Invocation(
        invocation_id="test-inv-001",
        user_content=Content(
            parts=[Part(text="What is 2+2?")],
            role="user"
        ),
        final_response=Content(
            parts=[Part(text="2 + 2 = 4")],
            role="assistant"
        ),
        intermediate_data=IntermediateData(),
        creation_timestamp=1704067200.0
    )

    # Create sample eval case
    eval_case = EvalCase(
        eval_id="test-case-001",
        conversation=[invocation],
        session_input=SessionInput(
            app_name="test_app",
            user_id="test_user",
            state={},
            user_prompt="What is 2+2?",
            system_instruction="You are a helpful assistant."
        ),
        creation_timestamp=1704067200.0
    )

    # Create provider result
    provider_result = ProviderResult(
        conversation_history=[invocation],
        cost=0.001,
        time_taken=1.5,
        token_usage={"input_tokens": 10, "output_tokens": 5},
        metadata={"model": "test-model"},
        success=True
    )

    # Create evaluator results
    evaluator_results = [
        EvaluatorResult(
            evaluator_name="test_evaluator",
            evaluator_type="response_evaluator",
            success=True,
            score=0.95,
            threshold=0.8,
            passed=True,
            details={"reason": "Response matches expected output"}
        )
    ]

    # Create execution run
    execution_run = ExecutionRun(
        execution_id="exec-001",
        run_number=1,
        eval_set_id="test-set-001",
        eval_case_id="test-case-001",
        provider_type="test_provider",
        provider_result=provider_result,
        evaluator_results=evaluator_results,
        overall_success=True,
        timestamp=datetime.now(),
        eval_case=eval_case
    )

    # Create evaluation report
    report = EvaluationReport(
        execution_runs=[execution_run],
        summary={"total_cases": 1, "passed": 1, "failed": 0},
        total_cost=0.001,
        total_time=1.5,
        success_rate=1.0,
        overall_success=True,
        generated_at=datetime.now()
    )

    return report

def verify_database(db_path: Path):
    """Verify database contents"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    print("\n📊 Database Verification:")
    print("-" * 50)

    # Check reports table
    cursor.execute("SELECT COUNT(*) FROM reports")
    report_count = cursor.fetchone()[0]
    print(f"✓ Reports table: {report_count} record(s)")

    cursor.execute("SELECT report_id, total_cost, total_time, success_rate FROM reports")
    for row in cursor.fetchall():
        print(f"  - Report ID: {row[0]}")
        print(f"    Cost: ${row[1]:.4f}, Time: {row[2]:.2f}s, Success Rate: {row[3]:.1%}")

    # Check execution_runs table
    cursor.execute("SELECT COUNT(*) FROM execution_runs")
    run_count = cursor.fetchone()[0]
    print(f"\n✓ Execution runs table: {run_count} record(s)")

    cursor.execute("""
        SELECT execution_id, eval_case_id, provider_type, overall_success, cost, time_taken
        FROM execution_runs
    """)
    for row in cursor.fetchall():
        print(f"  - Execution ID: {row[0]}")
        print(f"    Eval Case: {row[1]}, Provider: {row[2]}")
        print(f"    Success: {bool(row[3])}, Cost: ${row[4]:.4f}, Time: {row[5]:.2f}s")

    # Check evaluator_results table
    cursor.execute("SELECT COUNT(*) FROM evaluator_results")
    eval_count = cursor.fetchone()[0]
    print(f"\n✓ Evaluator results table: {eval_count} record(s)")

    cursor.execute("""
        SELECT evaluator_name, evaluator_type, success, passed, score, threshold
        FROM evaluator_results
    """)
    for row in cursor.fetchall():
        print(f"  - Evaluator: {row[0]} ({row[1]})")
        print(f"    Success: {bool(row[2])}, Passed: {bool(row[3])}")
        print(f"    Score: {row[4]:.2f}, Threshold: {row[5]:.2f}")

    # Verify indexes exist
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name LIKE 'idx_%'
    """)
    indexes = [row[0] for row in cursor.fetchall()]
    print(f"\n✓ Indexes created: {len(indexes)}")
    for idx in indexes:
        print(f"  - {idx}")

    conn.close()
    print("-" * 50)

def main():
    """Run direct database reporter test"""
    print("=" * 50)
    print("Database Reporter Direct Test")
    print("=" * 50)

    db_path = Path(__file__).parent / "test_direct_results.db"

    # Remove existing database if present
    if db_path.exists():
        db_path.unlink()
        print(f"🗑️  Removed existing database")

    try:
        # Create sample report
        print("\n📝 Creating sample evaluation report...")
        report = create_sample_report()
        print(f"✓ Created report with {len(report.execution_runs)} execution run(s)")

        # Initialize database reporter
        print(f"\n💾 Initializing database reporter...")
        print(f"   Database path: {db_path}")
        reporter = DatabaseReporter(db_path=str(db_path))

        # Generate report
        print("\n📤 Storing report to database...")
        reporter.generate_report(report)

        # Cleanup
        reporter.cleanup()
        print("✓ Report stored successfully")

        # Verify database was created
        if not db_path.exists():
            print(f"\n❌ ERROR: Database file was not created!")
            return 1

        print(f"\n✅ Database file created: {db_path}")
        print(f"   File size: {db_path.stat().st_size} bytes")

        # Verify database contents
        verify_database(db_path)

        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)

        return 0

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
