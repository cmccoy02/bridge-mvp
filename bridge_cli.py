import click
from dotenv import load_dotenv

load_dotenv()  # Load .env file

@click.command()
def test_env():
    """Check if .env is loaded"""
    token = os.getenv("GITHUB_TOKEN")
    click.echo(f"Token exists: {bool(token)}")

if __name__ == "__main__":
    cli = click.Group()
    cli.add_command(test_env)
    cli()