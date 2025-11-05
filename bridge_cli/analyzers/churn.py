"""Calculates code churn using Git history when available."""

import datetime
from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError

def analyze_churn(path: str, days: int = 30) -> dict:
    """
    Analyzes code churn over a given period.

    Args:
        path (str): The path to the Git repository.
        days (int): The number of days to look back for churn analysis.

    Returns:
        dict: A dictionary containing churn metrics.
    """
    try:
        repo = Repo(path)
    except (InvalidGitRepositoryError, NoSuchPathError):
        # Not a git repo or path invalid: return zeros so other analyzers can still run
        return {
            "total_commits": 0,
            "total_files_changed": 0,
            "recent_churned_files": [],
        }

    since_date = datetime.datetime.now() - datetime.timedelta(days=days)

    # Use HEAD explicitly; since accepts ISO8601 string
    commits = list(repo.iter_commits('HEAD', since=since_date.isoformat()))
    
    total_commits = len(commits)
    changed_files = set()
    
    for commit in commits:
        # For the initial commit, which has no parents
        if not commit.parents:
            for item in commit.tree.traverse():
                 if item.type == 'blob': # is a file
                    changed_files.add(item.path)
            continue

        diffs = commit.parents[0].diff(commit, create_patch=False)
        for diff in diffs:
            if diff.a_path:
                changed_files.add(diff.a_path)
            if diff.b_path:
                changed_files.add(diff.b_path)

    return {
        "total_commits": total_commits,
        "total_files_changed": len(changed_files),
        "recent_churned_files": sorted(list(changed_files))[:10],  # Show top 10 churned files
    } 