"""Utility functions for the Bridge CLI tool."""

import os
import tempfile
from pathlib import Path
from typing import Optional

from git import Repo
from git.exc import GitCommandError


def clone_repository(repo_url: str, target_dir: Optional[str] = None) -> str:
    """Clone a GitHub repository to a temporary or specified directory.
    
    Args:
        repo_url: The GitHub repository URL or owner/repo format
        target_dir: Optional directory to clone into. If None, uses a temp dir
        
    Returns:
        str: Path to the cloned repository
        
    Raises:
        GitCommandError: If cloning fails
    """
    # Convert owner/repo format to HTTPS URL if needed
    if not repo_url.startswith(('http://', 'https://', 'git://')):
        repo_url = f"https://github.com/{repo_url}.git"
    
    # Create temporary directory if no target specified
    if not target_dir:
        target_dir = tempfile.mkdtemp(prefix='bridge-cli-')
    else:
        target_dir = str(Path(target_dir).expanduser().resolve())
        os.makedirs(target_dir, exist_ok=True)
    
    try:
        Repo.clone_from(repo_url, target_dir)
        return target_dir
    except GitCommandError as e:
        raise GitCommandError(f"Failed to clone repository: {e}") 