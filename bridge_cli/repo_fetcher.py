"""Handles fetching repositories from local paths or remote sources.

Supports:
- Existing local directories (Git or non-Git)
- Remote Git URLs (https, http, git)
- GitHub shorthand in the form "owner/repo"
"""

import os
import shutil
import tempfile
from contextlib import contextmanager
from git import Repo

@contextmanager
def fetch_repo(repo_ref: str):
    """
    Provides a filesystem path for analysis. If given a local path, yields it
    directly. If given a remote reference, clones to a temporary directory and
    cleans up afterwards.

    This is a context manager, so it can be used with a 'with' statement.

    Args:
        repo_ref (str): Local directory path, full Git URL, or GitHub
                        shorthand ("owner/repo").

    Yields:
        str: The path to the temporary directory where the repo was cloned.
    
    Raises:
        GitCommandError: If cloning fails.
    """
    # 1) Local directory: yield directly (works for Git and non-Git repos)
    if os.path.exists(repo_ref) and os.path.isdir(repo_ref):
        yield os.path.abspath(repo_ref)
        return

    # 2) Remote: accept full URLs
    is_remote = repo_ref.startswith(("http://", "https://", "git://", "ssh://", "git@"))

    # 3) GitHub shorthand owner/repo
    github_shorthand = ("/" in repo_ref) and not is_remote

    if not (is_remote or github_shorthand):
        raise RuntimeError(
            "Invalid repository reference. Provide a local path, a full Git URL, or 'owner/repo'."
        )

    clone_url = repo_ref
    if github_shorthand:
        clone_url = f"https://github.com/{repo_ref}.git"

    temp_dir = tempfile.mkdtemp(prefix="bridge-cli-")
    try:
        Repo.clone_from(clone_url, temp_dir)
        yield temp_dir
    except Exception as e:
        # Normalize errors for the CLI to display
        raise RuntimeError(f"Failed to clone repository: {e}")
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)