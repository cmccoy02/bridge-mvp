"""Command-line interface for the Bridge CLI tool."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from typing import Optional

from bridge_cli.repo_fetcher import fetch_repo
from bridge_cli.analyzers.complexity import calculate_complexity
from bridge_cli.analyzers.churn import analyze_churn
from bridge_cli.analyzers.duplication import analyze_duplication
from bridge_cli.analyzers.security import analyze_security
from bridge_cli.report import generate_report
from bridge_cli.analyzers.overview import (
    get_repo_name,
    get_age_days_and_total_commits,
    language_breakdown,
    fetch_open_issues,
)
from bridge_cli.ascii_art import LOGO

@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx):
    """Bridge CLI - Analyze technical debt in local or remote Git repositories."""
    console = Console()
    if ctx.invoked_subcommand is None:
        rich_logo = Text.from_markup(f"[#FF4F00]{LOGO}[/#FF4F00]")
        aligned_logo = Align.center(rich_logo)
        console.print(aligned_logo)

        console.print("\nWelcome to BRIDGE!", justify="center")
        console.print("Get started by analyzing a repository:", justify="center")
        console.print("  [bold]bridge analyze <repo_url>[/bold]", justify="center")
        console.print("For more help, run:", justify="center")
        console.print("  [bold]bridge --help[/bold]", justify="center")






@cli.command()
@click.argument('repo_url')
@click.option('--output', '-o', type=click.Path(dir_okay=False), help='Write full JSON report to file')
def analyze(repo_url: str, output: Optional[str] = None):
    """
    Analyze technical debt in a Git repository.

    REPO_URL can be a remote URL (e.g., 'https://github.com/owner/repo.git')
    or a local path to a repository.
    """
    try:
        with fetch_repo(repo_url) as repo_path:
            console = Console()
            console.print(f"Analyzing repository in [bold]{repo_path}[/bold]...\n")

            # Core analyzers
            complexity_metrics = calculate_complexity(repo_path)
            churn_metrics = analyze_churn(repo_path)
            duplication_metrics = analyze_duplication(repo_path)
            security_metrics = analyze_security(repo_path)

            metrics = {
                "complexity": complexity_metrics,
                "churn": churn_metrics,
                "duplication": duplication_metrics,
                "security": security_metrics,
            }

            # Overview
            repo_name = get_repo_name(repo_url)
            age_days, total_commits = get_age_days_and_total_commits(repo_path)
            lang_pct = language_breakdown(repo_path, repo_url)
            open_issues = fetch_open_issues(repo_url)

            # Optional JSON output file
            if output:
                json_report = generate_report(repo_name, metrics)
                try:
                    with open(output, 'w', encoding='utf-8') as f:
                        f.write(json_report)
                    console.print(f"Saved detailed JSON report to [bold]{output}[/bold].\n")
                except OSError as err:
                    raise click.ClickException(f"Failed to write report: {err}")

            # Pretty summary
            table = Table.grid(padding=(0, 2))
            table.add_column(justify="right", style="bold cyan")
            table.add_column()

            # Name
            table.add_row("name:", repo_name)

            # Age
            age_str = "N/A" if age_days is None else f"{age_days} days"
            table.add_row("age:", age_str)

            # Languages (top 3)
            if lang_pct:
                top = ", ".join(f"{lang} {pct}%" for lang, pct in lang_pct[:3])
                table.add_row("language breakdown:", top)
            else:
                table.add_row("language breakdown:", "N/A")

            # Open issues
            table.add_row("open issues:", str(open_issues) if open_issues is not None else "N/A")

            # Commits
            table.add_row("commits:", str(total_commits))

            # Churn (last 30d)
            churn_desc = f"{churn_metrics.get('total_commits', 0)} commits, {churn_metrics.get('total_files_changed', 0)} files"
            table.add_row("churn (30d):", churn_desc)

            # Complexity
            avg_cx = complexity_metrics.get("average_complexity", 0.0)
            table.add_row("complexity:", f"avg {avg_cx}")

            panel = Panel(table, title=f"BRIDGE OVERVIEW • {repo_name}", border_style="#FF4F00")
            console.print(panel)

    except Exception as e:
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli() 