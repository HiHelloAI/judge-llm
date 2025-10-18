#!/usr/bin/env python3
"""
Advanced Database Queries - Demonstrates the full power of the enhanced database schema

This script showcases how to query complete evaluation history including:
- Full conversation tracking (expected vs actual responses)
- Time-based performance trends
- Test case investigation
- Score and threshold analysis
- Provider and model comparison
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


def query_database(db_path: str):
    """Run advanced queries on the database"""

    db_file = Path(db_path)
    if not db_file.exists():
        print(f"❌ Database not found: {db_path}")
        print(f"\nPlease run the evaluation first:")
        print(f"  python run_evaluation.py")
        return

    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 100)
    print("🔍 ADVANCED DATABASE ANALYSIS - Complete Evaluation History")
    print("=" * 100)

    # Query 1: Complete conversation investigation
    print("\n\n💬 CONVERSATION INVESTIGATION")
    print("-" * 100)
    print("Compare expected vs actual responses for each test case\n")

    cursor.execute("""
        SELECT
            er.execution_id,
            er.eval_case_id,
            ec.user_prompt,
            er.provider_type,
            er.provider_model,
            er.timestamp,
            er.overall_success
        FROM execution_runs er
        JOIN eval_cases ec ON er.eval_case_id = ec.eval_case_id
        ORDER BY er.timestamp DESC
        LIMIT 5
    """)

    for run in cursor.fetchall():
        print(f"\n{'='*100}")
        print(f"Execution: {run['execution_id']}")
        print(f"Test Case: {run['eval_case_id']}")
        print(f"Provider: {run['provider_type']} ({run['provider_model'] or 'N/A'})")
        print(f"Time: {run['timestamp']}")
        print(f"Success: {'✅' if run['overall_success'] else '❌'}")
        print(f"\nUser Prompt: {run['user_prompt']}")
        print(f"\n{'-'*100}")

        # Get expected and actual conversations
        cursor.execute("""
            SELECT invocation_type, user_message, assistant_message, sequence_order
            FROM invocations
            WHERE execution_id = ?
            ORDER BY invocation_type, sequence_order
        """, (run['execution_id'],))

        conversations = cursor.fetchall()

        expected_convs = [c for c in conversations if c['invocation_type'] == 'expected']
        actual_convs = [c for c in conversations if c['invocation_type'] == 'actual']

        print(f"\n📝 EXPECTED Response:")
        for conv in expected_convs:
            print(f"   {conv['assistant_message']}")

        print(f"\n🤖 ACTUAL Response:")
        for conv in actual_convs:
            print(f"   {conv['assistant_message']}")

        # Get evaluator results for this execution
        cursor.execute("""
            SELECT evaluator_name, passed, score, threshold
            FROM evaluator_results
            WHERE execution_id = ?
        """, (run['execution_id'],))

        eval_results = cursor.fetchall()
        if eval_results:
            print(f"\n🎯 Evaluator Results:")
            for er in eval_results:
                status = "✅ PASS" if er['passed'] else "❌ FAIL"
                score_info = f"Score: {er['score']:.2f}, Threshold: {er['threshold']:.2f}" if er['score'] is not None else ""
                print(f"   {status} - {er['evaluator_name']} {score_info}")

    # Query 2: Time-based performance trends
    print("\n\n" + "=" * 100)
    print("📈 TIME-BASED PERFORMANCE TRENDS")
    print("-" * 100)

    cursor.execute("""
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as num_runs,
            SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as successful,
            AVG(cost) as avg_cost,
            AVG(time_taken) as avg_time,
            AVG(input_tokens) as avg_input_tokens,
            AVG(output_tokens) as avg_output_tokens
        FROM execution_runs
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        LIMIT 10
    """)

    print(f"\n{'Date':<12} | {'Runs':>6} | {'Success':>10} | {'Avg Cost':>10} | {'Avg Time':>10} | {'Tokens (In/Out)':>20}")
    print("-" * 100)

    for row in cursor.fetchall():
        success_rate = (row['successful'] / row['num_runs'] * 100) if row['num_runs'] > 0 else 0
        tokens_info = f"{row['avg_input_tokens']:.0f} / {row['avg_output_tokens']:.0f}"
        print(f"{row['date']:<12} | {row['num_runs']:>6} | {row['successful']:>3} ({success_rate:>5.1f}%) | "
              f"${row['avg_cost']:>9.4f} | {row['avg_time']:>8.2f}s | {tokens_info:>20}")

    # Query 3: Test case deep dive with history
    print("\n\n" + "=" * 100)
    print("🧪 TEST CASE PERFORMANCE HISTORY")
    print("-" * 100)

    cursor.execute("""
        SELECT
            ec.eval_case_id,
            ec.user_prompt,
            COUNT(er.execution_id) as total_runs,
            SUM(CASE WHEN er.overall_success = 1 THEN 1 ELSE 0 END) as passed_runs,
            AVG(er.cost) as avg_cost,
            AVG(er.time_taken) as avg_time,
            MIN(er.timestamp) as first_run,
            MAX(er.timestamp) as last_run
        FROM eval_cases ec
        LEFT JOIN execution_runs er ON ec.eval_case_id = er.eval_case_id
        GROUP BY ec.eval_case_id
        ORDER BY total_runs DESC
    """)

    for row in cursor.fetchall():
        pass_rate = (row['passed_runs'] / row['total_runs'] * 100) if row['total_runs'] > 0 else 0
        status = "✅" if pass_rate == 100 else "⚠️" if pass_rate >= 50 else "❌"

        print(f"\n{status} {row['eval_case_id']}")
        print(f"   Prompt: {row['user_prompt'][:80]}...")
        print(f"   Runs: {row['total_runs']} | Pass Rate: {pass_rate:.0f}% ({row['passed_runs']}/{row['total_runs']})")
        print(f"   Avg Cost: ${row['avg_cost']:.4f} | Avg Time: {row['avg_time']:.2f}s")
        print(f"   First Run: {row['first_run']} | Last Run: {row['last_run']}")

    # Query 4: Provider & Model comparison
    print("\n\n" + "=" * 100)
    print("🤖 PROVIDER & MODEL COMPARISON")
    print("-" * 100)

    cursor.execute("""
        SELECT
            provider_type,
            provider_model,
            COUNT(*) as runs,
            SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as successful,
            AVG(cost) as avg_cost,
            SUM(cost) as total_cost,
            AVG(time_taken) as avg_time,
            AVG(input_tokens) as avg_input_tokens,
            AVG(output_tokens) as avg_output_tokens
        FROM execution_runs
        GROUP BY provider_type, provider_model
        ORDER BY runs DESC
    """)

    print(f"\n{'Provider':<15} | {'Model':<25} | {'Runs':>6} | {'Success':>10} | {'Total Cost':>12} | {'Avg Time':>10} | {'Tokens':>15}")
    print("-" * 100)

    for row in cursor.fetchall():
        success_rate = (row['successful'] / row['runs'] * 100) if row['runs'] > 0 else 0
        model = row['provider_model'] or 'N/A'
        tokens = f"{row['avg_input_tokens']:.0f}/{row['avg_output_tokens']:.0f}"
        print(f"{row['provider_type']:<15} | {model:<25} | {row['runs']:>6} | "
              f"{row['successful']:>3} ({success_rate:>5.1f}%) | ${row['total_cost']:>11.4f} | "
              f"{row['avg_time']:>8.2f}s | {tokens:>15}")

    # Query 5: Evaluator performance with score distribution
    print("\n\n" + "=" * 100)
    print("🎯 EVALUATOR PERFORMANCE & SCORE DISTRIBUTION")
    print("-" * 100)

    cursor.execute("""
        SELECT
            evaluator_name,
            evaluator_type,
            COUNT(*) as total,
            SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
            AVG(score) as avg_score,
            MIN(score) as min_score,
            MAX(score) as max_score,
            AVG(threshold) as avg_threshold
        FROM evaluator_results
        WHERE score IS NOT NULL
        GROUP BY evaluator_name, evaluator_type
    """)

    for row in cursor.fetchall():
        pass_rate = (row['passed'] / row['total'] * 100) if row['total'] > 0 else 0
        print(f"\n{row['evaluator_name']} ({row['evaluator_type']})")
        print(f"   Total Evaluations: {row['total']}")
        print(f"   Pass Rate: {pass_rate:.1f}% ({row['passed']}/{row['total']})")
        print(f"   Score Range: {row['min_score']:.2f} - {row['max_score']:.2f} (avg: {row['avg_score']:.2f})")
        print(f"   Avg Threshold: {row['avg_threshold']:.2f}")

    # Query 6: Failed test investigation
    print("\n\n" + "=" * 100)
    print("❌ FAILED TEST INVESTIGATION")
    print("-" * 100)

    cursor.execute("""
        SELECT
            er.execution_id,
            er.eval_case_id,
            ec.user_prompt,
            er.provider_type,
            er.timestamp,
            eval_res.evaluator_name,
            eval_res.score,
            eval_res.threshold,
            eval_res.error
        FROM execution_runs er
        JOIN eval_cases ec ON er.eval_case_id = ec.eval_case_id
        JOIN evaluator_results eval_res ON er.execution_id = eval_res.execution_id
        WHERE eval_res.passed = 0
        ORDER BY er.timestamp DESC
        LIMIT 10
    """)

    failures = cursor.fetchall()
    if failures:
        for i, failure in enumerate(failures, 1):
            print(f"\n{i}. {failure['execution_id']} - {failure['eval_case_id']}")
            print(f"   Prompt: {failure['user_prompt'][:80]}...")
            print(f"   Provider: {failure['provider_type']}")
            print(f"   Time: {failure['timestamp']}")
            print(f"   Evaluator: {failure['evaluator_name']}")
            if failure['score'] is not None:
                print(f"   Score: {failure['score']:.2f} (threshold: {failure['threshold']:.2f})")
            if failure['error']:
                print(f"   Error: {failure['error']}")
    else:
        print("\n✅ No failed evaluations found!")

    # Query 7: Cost analysis by test case
    print("\n\n" + "=" * 100)
    print("💰 COST ANALYSIS BY TEST CASE")
    print("-" * 100)

    cursor.execute("""
        SELECT
            ec.eval_case_id,
            ec.user_prompt,
            COUNT(er.execution_id) as runs,
            SUM(er.cost) as total_cost,
            AVG(er.cost) as avg_cost,
            SUM(er.total_tokens) as total_tokens
        FROM eval_cases ec
        JOIN execution_runs er ON ec.eval_case_id = er.eval_case_id
        GROUP BY ec.eval_case_id
        ORDER BY total_cost DESC
        LIMIT 10
    """)

    print(f"\n{'Test Case':<20} | {'Runs':>6} | {'Total Cost':>12} | {'Avg Cost':>10} | {'Total Tokens':>15}")
    print("-" * 100)

    for row in cursor.fetchall():
        print(f"{row['eval_case_id']:<20} | {row['runs']:>6} | ${row['total_cost']:>11.4f} | "
              f"${row['avg_cost']:>9.4f} | {row['total_tokens']:>15}")

    conn.close()
    print("\n" + "=" * 100)


def main():
    """Main function"""
    import sys

    # Use default database path
    default_db = Path(__file__).parent.parent.parent / "reports" / "06-database-reporter" / "results.db"

    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = str(default_db)

    query_database(db_path)

    print("\n💡 The enhanced database schema enables:")
    print("   • Complete conversation history (expected vs actual)")
    print("   • Time-based trend analysis")
    print("   • Test case performance tracking")
    print("   • Provider and model comparison")
    print("   • Detailed failure investigation")
    print("   • Cost breakdown by test case")
    print("   • Score distribution analysis")
    print("\n🚀 Use this data to build custom dashboards and monitoring systems!")
    print()


if __name__ == "__main__":
    main()
