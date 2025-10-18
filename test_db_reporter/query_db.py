#!/usr/bin/env python3
"""Example script to query the database"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def query_database(db_path: str):
    """Query and display database contents"""

    db_file = Path(db_path)
    if not db_file.exists():
        print(f"❌ Database not found: {db_path}")
        return

    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()

    print("=" * 80)
    print(f"📊 Query Results from: {db_path}")
    print("=" * 80)

    # Query 1: All reports summary
    print("\n📋 REPORTS SUMMARY")
    print("-" * 80)
    cursor.execute("""
        SELECT
            report_id,
            generated_at,
            total_cost,
            total_time,
            success_rate,
            overall_success
        FROM reports
        ORDER BY generated_at DESC
    """)

    for row in cursor.fetchall():
        print(f"\nReport: {row['report_id']}")
        print(f"  Generated: {row['generated_at']}")
        print(f"  Total Cost: ${row['total_cost']:.4f}")
        print(f"  Total Time: {row['total_time']:.2f}s")
        print(f"  Success Rate: {row['success_rate']:.1%}")
        print(f"  Overall Success: {'✅' if row['overall_success'] else '❌'}")

    # Query 2: Execution runs by provider
    print("\n\n🚀 EXECUTION RUNS BY PROVIDER")
    print("-" * 80)
    cursor.execute("""
        SELECT
            provider_type,
            COUNT(*) as total_runs,
            SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as successful_runs,
            AVG(cost) as avg_cost,
            AVG(time_taken) as avg_time
        FROM execution_runs
        GROUP BY provider_type
    """)

    for row in cursor.fetchall():
        success_rate = (row['successful_runs'] / row['total_runs'] * 100) if row['total_runs'] > 0 else 0
        print(f"\nProvider: {row['provider_type']}")
        print(f"  Total Runs: {row['total_runs']}")
        print(f"  Successful: {row['successful_runs']} ({success_rate:.1f}%)")
        print(f"  Avg Cost: ${row['avg_cost']:.4f}")
        print(f"  Avg Time: {row['avg_time']:.2f}s")

    # Query 3: Recent execution runs
    print("\n\n📝 RECENT EXECUTION RUNS (Last 10)")
    print("-" * 80)
    cursor.execute("""
        SELECT
            execution_id,
            eval_case_id,
            provider_type,
            overall_success,
            cost,
            time_taken,
            timestamp
        FROM execution_runs
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        print(f"\nExecution: {row['execution_id']}")
        print(f"  Eval Case: {row['eval_case_id']}")
        print(f"  Provider: {row['provider_type']}")
        print(f"  Success: {'✅' if row['overall_success'] else '❌'}")
        print(f"  Cost: ${row['cost']:.4f} | Time: {row['time_taken']:.2f}s")
        print(f"  Timestamp: {row['timestamp']}")

    # Query 4: Evaluator performance
    print("\n\n🎯 EVALUATOR PERFORMANCE")
    print("-" * 80)
    cursor.execute("""
        SELECT
            evaluator_name,
            evaluator_type,
            COUNT(*) as total_evaluations,
            SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed_count,
            AVG(score) as avg_score,
            AVG(threshold) as avg_threshold
        FROM evaluator_results
        GROUP BY evaluator_name, evaluator_type
    """)

    for row in cursor.fetchall():
        pass_rate = (row['passed_count'] / row['total_evaluations'] * 100) if row['total_evaluations'] > 0 else 0
        print(f"\nEvaluator: {row['evaluator_name']} ({row['evaluator_type']})")
        print(f"  Total Evaluations: {row['total_evaluations']}")
        print(f"  Passed: {row['passed_count']} ({pass_rate:.1f}%)")
        if row['avg_score'] is not None:
            print(f"  Avg Score: {row['avg_score']:.2f}")
        if row['avg_threshold'] is not None:
            print(f"  Avg Threshold: {row['avg_threshold']:.2f}")

    # Query 5: Failed evaluations (if any)
    print("\n\n❌ FAILED EVALUATIONS")
    print("-" * 80)
    cursor.execute("""
        SELECT
            er.evaluator_name,
            er.evaluator_type,
            er.error,
            ex.execution_id,
            ex.eval_case_id,
            ex.provider_type
        FROM evaluator_results er
        JOIN execution_runs ex ON er.execution_id = ex.execution_id
        WHERE er.passed = 0
        ORDER BY ex.timestamp DESC
        LIMIT 10
    """)

    failed_count = 0
    for row in cursor.fetchall():
        failed_count += 1
        print(f"\n{failed_count}. Evaluator: {row['evaluator_name']} ({row['evaluator_type']})")
        print(f"   Execution: {row['execution_id']}")
        print(f"   Eval Case: {row['eval_case_id']}")
        print(f"   Provider: {row['provider_type']}")
        if row['error']:
            print(f"   Error: {row['error']}")

    if failed_count == 0:
        print("\n✅ No failed evaluations found!")

    # Query 6: Cost and time trends
    print("\n\n💰 COST & TIME ANALYSIS")
    print("-" * 80)
    cursor.execute("""
        SELECT
            COUNT(*) as total_runs,
            SUM(cost) as total_cost,
            AVG(cost) as avg_cost,
            MIN(cost) as min_cost,
            MAX(cost) as max_cost,
            SUM(time_taken) as total_time,
            AVG(time_taken) as avg_time,
            MIN(time_taken) as min_time,
            MAX(time_taken) as max_time
        FROM execution_runs
    """)

    row = cursor.fetchone()
    if row and row['total_runs'] > 0:
        print(f"\nTotal Runs: {row['total_runs']}")
        print(f"\nCost Metrics:")
        print(f"  Total: ${row['total_cost']:.4f}")
        print(f"  Average: ${row['avg_cost']:.4f}")
        print(f"  Min: ${row['min_cost']:.4f} | Max: ${row['max_cost']:.4f}")
        print(f"\nTime Metrics:")
        print(f"  Total: {row['total_time']:.2f}s")
        print(f"  Average: {row['avg_time']:.2f}s")
        print(f"  Min: {row['min_time']:.2f}s | Max: {row['max_time']:.2f}s")

    conn.close()
    print("\n" + "=" * 80)

def main():
    """Main function"""
    import sys

    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Default to test database
        db_path = Path(__file__).parent / "test_direct_results.db"

    query_database(str(db_path))

if __name__ == "__main__":
    main()
