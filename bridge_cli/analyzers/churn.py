"""Calculates code churn using Git history when available."""

import datetime
from collections import Counter, defaultdict
from typing import Dict, List
from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError

def _monday(dt: datetime.datetime) -> datetime.date:
    d = dt.date()
    return d - datetime.timedelta(days=d.weekday())


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
            "weekly_commits": [],
            "top_churned_files": [],
            "top_churned_dirs": [],
            "authors_count": 0,
        }

    since_date = datetime.datetime.now() - datetime.timedelta(days=days)

    # Use HEAD explicitly; since accepts ISO8601 string
    commits = list(repo.iter_commits('HEAD', since=since_date.isoformat()))

    total_commits = len(commits)
    changed_files = set()
    file_touches: Counter = Counter()
    dir_touches: Counter = Counter()
    weekly: Dict[datetime.date, int] = defaultdict(int)
    authors: Counter = Counter()

    for commit in commits:
        # Author
        try:
            author_id = (commit.author.email or commit.author.name or 'unknown').lower()
        except Exception:
            author_id = 'unknown'
        authors[author_id] += 1

        # Weekly bucket
        try:
            c_dt = datetime.datetime.fromtimestamp(commit.committed_date)
        except Exception:
            c_dt = datetime.datetime.now()
        weekly[_monday(c_dt)] += 1

        # For the initial commit, which has no parents
        if not commit.parents:
            for item in commit.tree.traverse():
                if getattr(item, 'type', None) == 'blob':
                    path_str = item.path
                    changed_files.add(path_str)
                    file_touches[path_str] += 1
                    top = path_str.split('/', 1)[0]
                    dir_touches[top] += 1
            continue

        diffs = commit.parents[0].diff(commit, create_patch=False)
        for diff in diffs:
            for p in (diff.a_path, diff.b_path):
                if not p:
                    continue
                changed_files.add(p)
                file_touches[p] += 1
                top = p.split('/', 1)[0]
                dir_touches[top] += 1

    weekly_commits = [{"week_start": d.isoformat(), "commits": weekly[d]} for d in sorted(weekly.keys())]

    return {
        "total_commits": total_commits,
        "total_files_changed": len(changed_files),
        "recent_churned_files": sorted(list(changed_files))[:10],
        "weekly_commits": weekly_commits,
        "top_churned_files": [{"path": p, "touches": c} for p, c in file_touches.most_common(10)],
        "top_churned_dirs": [{"dir": d, "touches": c} for d, c in dir_touches.most_common(10)],
        "authors_count": len(authors),
    }