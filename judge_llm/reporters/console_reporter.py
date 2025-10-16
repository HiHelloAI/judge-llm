"""Console reporter"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from judge_llm.core.models import EvaluationReport
from judge_llm.reporters.base import BaseReporter
from judge_llm.utils.logger import get_logger


class ConsoleReporter(BaseReporter):
    """Report evaluation results to console"""

    def __init__(self):
        self.console = Console()
        self.logger = get_logger()

    def generate_report(self, report: EvaluationReport):
        """Generate console report

        Args:
            report: EvaluationReport object
        """
        self.logger.info("Generating console report")

        # Print header
        self.console.print("\n")
        self.console.print(Panel.fit(
            "[bold cyan]Judge LLM Evaluation Report[/bold cyan]",
            border_style="cyan"
        ))

        # Print summary
        self._print_summary(report)

        # Print execution details
        self._print_execution_details(report)

        # Print footer
        status_color = "green" if report.overall_success else "red"
        status_text = "✓ PASSED" if report.overall_success else "✗ FAILED"
        self.console.print(f"\n[{status_color}]Overall Status: {status_text}[/{status_color}]\n")

    def _print_summary(self, report: EvaluationReport):
        """Print summary statistics"""
        summary_table = Table(title="Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="yellow")

        summary_table.add_row("Total Executions", str(len(report.execution_runs)))
        summary_table.add_row("Success Rate", f"{report.success_rate:.1%}")
        summary_table.add_row("Total Cost", f"${report.total_cost:.4f}")
        summary_table.add_row("Total Time", f"{report.total_time:.2f}s")

        avg_time = report.total_time / len(report.execution_runs) if report.execution_runs else 0
        summary_table.add_row("Avg Time/Execution", f"{avg_time:.2f}s")

        self.console.print("\n")
        self.console.print(summary_table)

    def _print_execution_details(self, report: EvaluationReport):
        """Print execution details"""
        details_table = Table(
            title="Execution Details",
            show_header=True,
            header_style="bold magenta"
        )
        details_table.add_column("Exec ID", style="cyan", no_wrap=True)
        details_table.add_column("Eval Case", style="blue")
        details_table.add_column("Run #", justify="right")
        details_table.add_column("Provider", style="yellow")
        details_table.add_column("Status", justify="center")
        details_table.add_column("Time (s)", justify="right")
        details_table.add_column("Cost ($)", justify="right")
        details_table.add_column("Evaluators", justify="center")

        for exec_run in report.execution_runs:
            status_emoji = "✓" if exec_run.overall_success else "✗"
            status_color = "green" if exec_run.overall_success else "red"

            passed_evaluators = sum(1 for e in exec_run.evaluator_results if e.passed)
            total_evaluators = len(exec_run.evaluator_results)
            eval_status = f"{passed_evaluators}/{total_evaluators}"

            details_table.add_row(
                exec_run.execution_id[:8],
                exec_run.eval_case_id[:12],
                str(exec_run.run_number),
                exec_run.provider_type,
                f"[{status_color}]{status_emoji}[/{status_color}]",
                f"{exec_run.provider_result.time_taken:.2f}",
                f"{exec_run.provider_result.cost:.4f}",
                eval_status,
            )

        self.console.print("\n")
        self.console.print(details_table)

    def cleanup(self):
        """Cleanup resources"""
        pass
