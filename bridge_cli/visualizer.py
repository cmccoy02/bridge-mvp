"""Visualization functionality for the Bridge CLI tool."""

from datetime import datetime
from typing import Dict, Any
from zoneinfo import ZoneInfo

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def create_metrics_table(metrics: Dict[str, Any]) -> Table:
    """Create a rich table for displaying metrics."""
    table = Table(title="Technical Debt Metrics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Weight", style="green")
    
    # Add core metrics
    table.add_row(
        "Complexity Score",
        f"{metrics['complexity_score']:.2f}",
        "50%"
    )
    table.add_row(
        "Open Issues",
        str(metrics['open_issues']),
        "30%"
    )
    table.add_row(
        "Security Issues",
        str(metrics['security_issues']),
        "20%"
    )
    if metrics['test_coverage'] is not None:
        table.add_row(
            "Test Coverage",
            f"{metrics['test_coverage']:.1f}%",
            "N/A"
        )
    
    return table


def create_issues_breakdown(issues: Dict[str, int]) -> Table:
    """Create a table showing issue breakdown."""
    table = Table(title="Issues Breakdown", show_header=True)
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="magenta")
    
    table.add_row("Total Issues", str(issues['total']))
    table.add_row("Bugs", str(issues['bugs']))
    table.add_row("Technical Debt", str(issues['tech_debt']))
    
    return table


def create_repo_metadata(metadata: Dict[str, Any]) -> Table:
    """Create a table showing repository metadata."""
    table = Table(title="Repository Information", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    # Format the repository age
    created_date = metadata.get('created_at')
    if created_date:
        now = datetime.now(ZoneInfo("UTC"))
        age = now - created_date
        age_str = f"{age.days} days ({age.days // 365} years, {age.days % 365} days)"
    else:
        age_str = "Unknown"
    
    # Format the last commit date
    last_commit = metadata.get('last_commit_at')
    if last_commit:
        last_commit_str = last_commit.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        last_commit_str = "Unknown"
    
    table.add_row("Repository Age", age_str)
    table.add_row("Last Commit", last_commit_str)
    table.add_row("Primary Language", metadata.get('primary_language', 'Unknown'))
    
    return table


def display_results(results: Dict[str, Any], json_output: bool = False) -> None:
    """Display analysis results in the terminal or as JSON."""
    if json_output:
        console.print_json(data=results)
        return
    
    # Create header with final score
    score = results['final_score']
    score_color = (
        "cyan" if score <= 25 else
        "green" if score <= 50 else
        "yellow" if score <= 75 else
        "red"
    )
    header = Panel(
        f"[bold white]Technical Debt Score:[/] [bold {score_color}]{score:.1f}[/]",
        subtitle="[dim](Scored on a scale of 0-100, WIP)[/]"
    )
    console.print(header)
    
    # Display metrics table
    console.print(create_metrics_table(results))
    
    # Display issues breakdown
    if 'details' in results and 'issues_breakdown' in results['details']:
        console.print(create_issues_breakdown(results['details']['issues_breakdown']))
    
    # Display repository metadata
    if 'metadata' in results:
        console.print(create_repo_metadata(results['metadata']))


def create_progress_context() -> Progress:
    """Create a progress context for long-running operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) 