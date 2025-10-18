#!/usr/bin/env python3
"""
Generate standalone HTML dashboard for viewing SQLite evaluation results

This script creates a self-contained HTML file that can load and visualize
your Judge LLM evaluation database. Everything runs locally in the browser,
no server or external services required!
"""

from pathlib import Path
import shutil


def generate_dashboard(output_path: str = "./dashboard.html"):
    """
    Generate standalone HTML dashboard

    Args:
        output_path: Where to save the dashboard HTML file
    """
    # Get the template from judge_llm package
    template_path = Path(__file__).parent.parent.parent / "judge_llm" / "templates" / "monitor.html"

    if not template_path.exists():
        print(f"❌ Template not found at: {template_path}")
        return False

    # Copy to output location
    output_file = Path(output_path).expanduser().resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy(template_path, output_file)

    print("=" * 80)
    print("✅ Dashboard Generated Successfully!")
    print("=" * 80)
    print()
    print(f"📁 Dashboard file: {output_file}")
    print()
    print("📖 How to use:")
    print("   1. Open the dashboard HTML file in your web browser")
    print("   2. Drag and drop your .db file (or click to browse)")
    print("   3. Explore your evaluation results!")
    print()
    print("🔒 Privacy:")
    print("   • All data stays local in your browser")
    print("   • No external services or uploads")
    print("   • Works completely offline")
    print()
    print("📊 Features:")
    print("   • Interactive stats overview")
    print("   • Execution history with details")
    print("   • Provider performance comparison")
    print("   • Test case analysis")
    print("   • Evaluator score tracking")
    print("   • Conversation comparison (expected vs actual)")
    print("   • Performance trends with charts")
    print()
    print("=" * 80)

    return True


def main():
    """Main function"""
    import sys

    output_path = sys.argv[1] if len(sys.argv) > 1 else "./dashboard.html"

    if generate_dashboard(output_path):
        print("\n💡 Tip: You can also access the dashboard template at:")
        print("   judge_llm/templates/monitor.html")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
