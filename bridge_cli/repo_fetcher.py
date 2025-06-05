"""Handles cloning of Git repositories."""

import os
import shutil
import tempfile
from contextlib import contextmanager
from git import Repo, GitCommandError

@contextmanager
def fetch_repo(repo_url: str):
    """
    Clones a repository to a temporary directory and cleans up afterwards.

    This is a context manager, so it can be used with a 'with' statement.

    Args:
        repo_url (str): The URL of the repository to clone.

    Yields:
        str: The path to the temporary directory where the repo was cloned.
    
    Raises:
        GitCommandError: If cloning fails.
    """
    if not repo_url.startswith(('http://', 'https://', 'git://')):
        repo_url = f"https://github.com/{repo_url}.git"

    temp_dir = tempfile.mkdtemp(prefix="bridge-cli-")
    try:
        Repo.clone_from(repo_url, temp_dir)
        yield temp_dir
    except GitCommandError as e:
        raise GitCommandError(f"Failed to clone repository: {e}")
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir) 