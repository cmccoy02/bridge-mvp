"""Command-line interface for the Bridge CLI tool."""

import os
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from bridge_cli.analyzer import RepoAnalyzer
from bridge_cli.visualizer import display_results, create_progress_context

# Load environment variables from the bridge_cli directory
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


def get_github_token() -> str:
    """Get GitHub token from environment or prompt user."""
    token = os.getenv("GITHUB_TOKEN")
    if not token or token == 'your_token_here':
        raise click.ClickException(
            "GitHub token not found. Please set GITHUB_TOKEN in bridge_cli/.env"
        )
    return token


@click.group()
@click.version_option()
def cli():
    """Bridge CLI - Analyze technical debt in GitHub repositories."""
    pass


@cli.command()
@click.argument('repo_url')
@click.option(
    '--json',
    is_flag=True,
    help='Output results in JSON format'
)
def analyze(repo_url: str, json: bool):
    """Analyze technical debt in a GitHub repository.
    
    REPO_URL should be in the format: owner/repository
    """
    try:
        # Get GitHub token
        token = get_github_token()
        
        # Create analyzer
        analyzer = RepoAnalyzer(token)
        
        # Show progress
        with create_progress_context() as progress:
            progress.add_task(description="Analyzing repository...")
            results = analyzer.analyze_repo(repo_url)
        
        # Display results
        display_results(results.__dict__, json)
        
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
def test_token():
    """Test if GitHub token is configured correctly."""
    try:
        token = get_github_token()
        click.echo(f"GitHub token found: {bool(token)}")
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == '__main__':
    cli() 