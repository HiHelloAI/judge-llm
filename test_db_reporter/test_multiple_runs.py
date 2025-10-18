#!/usr/bin/env python3
"""Test multiple evaluation runs appending to the same database"""

import sys
from pathlib import Path
from datetime import datetime
import sqlite3
import time

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

def create_sample_report(run_id: int, provider: str, success: bool) -> EvaluationReport:
    """Create a sample evaluation report"""

    invocation = Invocation(
        invocation_id=f"inv-{run_id}",
        user_content=Content(
            parts=[Part(text=f"Test prompt {run_id}")],
            role="user"
        ),
        final_response=Content(
            parts=[Part(text=f"Test response {run_id}")],
            role="assistant"
        ),
        intermediate_data=IntermediateData(),
        creation_timestamp=time.time()
    )

    eval_case = EvalCase(
        eval_id=f"case-{run_id}",
        conversation=[invocation],
        session_input=SessionInput(
            app_name="test_app",
            user_id=f"user_{run_id}",
            state={},
            user_prompt=f"Test prompt {run_id}",
            system_instruction="You are a helpful assistant."
        ),
        creation_timestamp=time.time()
    )

    provider_result = ProviderResult(
        conversation_history=[invocation],
        cost=0.001 * run_id,
        time_taken=1.0 + (run_id * 0.5),
        token_usage={"input_tokens": 10 + run_id, "output_tokens": 5 + run_id},
        metadata={"model": f"{provider}-model-v1"},
        success=success
    )

    evaluator_results = [
        EvaluatorResult(
            evaluator_name="accuracy_check",
            evaluator_type="response_evaluator",
            success=True,
            score=0.85 + (run_id * 0.01),
            threshold=0.8,
            passed=success,
            details={"reason": f"Test evaluation {run_id}"}
        )
    ]

    execution_run = ExecutionRun(
        execution_id=f"exec-{run_id}",
        run_number=1,
        eval_set_id=f"set-{run_id}",
        eval_case_id=f"case-{run_id}",
        provider_type=provider,
        provider_result=provider_result,
        evaluator_results=evaluator_results,
        overall_success=success,
        timestamp=datetime.now(),
        eval_case=eval_case
    )

    report = EvaluationReport(
        execution_runs=[execution_run],
        summary={"run_id": run_id, "provider": provider},
        total_cost=provider_result.cost,
        total_time=provider_result.time_taken,
        success_rate=1.0 if success else 0.0,
        overall_success=success,
        generated_at=datetime.now()
    )

    return report

def main():
    """Run multiple evaluations to same database"""
    print("=" * 80)
    print("Multiple Evaluation Runs Test")
    print("=" * 80)

    db_path = Path(__file__).parent / "test_multiple_runs.db"

    # Remove existing database
    if db_path.exists():
        db_path.unlink()
        print(f"🗑️  Removed existing database\n")

    # Create multiple evaluation runs
    test_cases = [
        (1, "gemini", True),
        (2, "openai", True),
        (3, "gemini", False),
        (4, "anthropic", True),
        (5, "openai", True),
    ]

    print(f"💾 Database: {db_path}\n")
    print(f"Running {len(test_cases)} evaluation(s)...\n")

    for run_id, provider, success in test_cases:
        print(f"📝 Run #{run_id}: provider={provider}, success={success}")

        # Create and store report
        report = create_sample_report(run_id, provider, success)
        reporter = DatabaseReporter(db_path=str(db_path))
        reporter.generate_report(report)
        reporter.cleanup()

        print(f"   ✓ Stored to database")

    # Verify database contents
    print("\n" + "=" * 80)
    print("📊 Database Verification")
    print("=" * 80)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Count records in each table
    cursor.execute("SELECT COUNT(*) FROM reports")
    report_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM execution_runs")
    run_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM evaluator_results")
    eval_count = cursor.fetchone()[0]

    print(f"\n✓ Reports: {report_count}")
    print(f"✓ Execution Runs: {run_count}")
    print(f"✓ Evaluator Results: {eval_count}")

    # Show summary by provider
    print("\n\n🚀 SUMMARY BY PROVIDER")
    print("-" * 80)
    cursor.execute("""
        SELECT
            provider_type,
            COUNT(*) as total,
            SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as successful,
            SUM(cost) as total_cost,
            AVG(time_taken) as avg_time
        FROM execution_runs
        GROUP BY provider_type
        ORDER BY provider_type
    """)

    for row in cursor.fetchall():
        provider, total, successful, cost, avg_time = row
        success_rate = (successful / total * 100) if total > 0 else 0
        print(f"\n{provider}:")
        print(f"  Runs: {total} | Success: {successful} ({success_rate:.0f}%)")
        print(f"  Cost: ${cost:.4f} | Avg Time: {avg_time:.2f}s")

    # Show cost trend
    print("\n\n💰 COST TREND")
    print("-" * 80)
    cursor.execute("""
        SELECT
            execution_id,
            provider_type,
            cost,
            timestamp
        FROM execution_runs
        ORDER BY timestamp
    """)

    total_cost = 0.0
    for row in cursor.fetchall():
        exec_id, provider, cost, timestamp = row
        total_cost += cost
        print(f"{exec_id}: {provider:12} - ${cost:.4f} (cumulative: ${total_cost:.4f})")

    conn.close()

    print("\n" + "=" * 80)
    print("✅ Test completed successfully!")
    print(f"📁 Database file: {db_path}")
    print(f"📊 Total records: {report_count} reports, {run_count} runs, {eval_count} evaluations")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
