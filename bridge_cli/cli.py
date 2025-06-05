"""Command-line interface for the Bridge CLI tool."""

import click

from bridge_cli.repo_fetcher import fetch_repo
from bridge_cli.analyzers.complexity import calculate_complexity
from bridge_cli.analyzers.churn import analyze_churn
from bridge_cli.analyzers.duplication import analyze_duplication
from bridge_cli.analyzers.security import analyze_security
from bridge_cli.report import generate_report

@click.group()
@click.version_option()
def cli():
    """Bridge CLI - Analyze technical debt in local or remote Git repositories."""
    pass

@cli.command()
@click.argument('repo_url')
def analyze(repo_url: str):
    """
    Analyze technical debt in a Git repository.

    REPO_URL can be a remote URL (e.g., 'https://github.com/owner/repo.git')
    or a local path to a repository.
    """
    try:
        with fetch_repo(repo_url) as repo_path:
            click.echo(f"Analyzing repository in {repo_path}...")

            metrics = {
                "complexity": calculate_complexity(repo_path),
                "churn": analyze_churn(repo_path),
                "duplication": analyze_duplication(repo_path),
                "security": analyze_security(repo_path),
            }

            repo_name = repo_url.split('/')[-1].replace('.git', '')
            report = generate_report(repo_name, metrics)

            click.echo(report)

    except Exception as e:
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli() 