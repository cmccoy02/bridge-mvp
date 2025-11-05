"""Repository overview metrics: name, age, languages, commits, open issues.

All functions are resilient to missing Git or network. They return sensible
defaults so the CLI can always render a summary.
"""

import os
import time
from typing import Dict, List, Optional, Tuple

# Defer optional imports for resilience
try:
    from git import Repo
    from git.exc import InvalidGitRepositoryError, NoSuchPathError
except Exception:  # pragma: no cover - environment without GitPython
    Repo = None  # type: ignore
    InvalidGitRepositoryError = Exception  # type: ignore
    NoSuchPathError = Exception  # type: ignore

try:
    import requests
except Exception:  # pragma: no cover - requests should exist, but fail gracefully
    requests = None  # type: ignore


def parse_github_full_name(repo_ref: str) -> Optional[str]:
    """Extract "owner/repo" from a reference if it's GitHub-like.

    Returns None if it cannot be parsed.
    """
    if "github.com" in repo_ref:
        parts = repo_ref.rstrip("/")
        if parts.endswith(".git"):
            parts = parts[:-4]
        try:
            owner, repo = parts.split("github.com/")[-1].split("/")[:2]
            return f"{owner}/{repo}"
        except ValueError:
            return None
    # Shorthand owner/repo
    if repo_ref.count("/") == 1 and "://" not in repo_ref:
        owner, repo = repo_ref.split("/")
        if owner and repo and not repo.endswith(".git"):
            return f"{owner}/{repo}"
        if owner and repo.endswith(".git"):
            return f"{owner}/{repo[:-4]}"
    return None


def get_repo_name(repo_ref: str) -> str:
    """Best-effort repository name from ref/path/URL."""
    # URL or owner/repo
    gh_full = parse_github_full_name(repo_ref)
    if gh_full:
        return gh_full.split("/")[-1]
    # Local path
    base = os.path.basename(os.path.abspath(repo_ref))
    if base:
        return base.replace(".git", "")
    return "unknown"


def get_age_days_and_total_commits(path: str) -> Tuple[Optional[int], int]:
    """Compute repo age in days and total commits. Returns (age_days, total_commits).

    age_days is None for non-git directories.
    """
    if Repo is None:
        return None, 0
    try:
        repo = Repo(path)
        commits = list(repo.iter_commits("HEAD"))
        if not commits:
            return 0, 0
        first = commits[-1].committed_date
        now = int(time.time())
        age_days = max(0, int((now - first) / 86400))
        return age_days, len(commits)
    except (InvalidGitRepositoryError, NoSuchPathError, Exception):
        return None, 0


_EXT_TO_LANG: Dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".go": "Go",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".php": "PHP",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cs": "C#",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".scala": "Scala",
    ".sh": "Shell",
    ".sql": "SQL",
    ".yml": "YAML",
    ".yaml": "YAML",
}

_IGNORE_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}


def _local_language_bytes(path: str) -> Dict[str, int]:
    totals: Dict[str, int] = {}
    for root, dirs, files in os.walk(path):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in _IGNORE_DIRS]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            lang = _EXT_TO_LANG.get(ext)
            if not lang:
                continue
            fp = os.path.join(root, fname)
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            totals[lang] = totals.get(lang, 0) + size
    return totals


def total_lines_of_code(path: str) -> int:
    """Count total lines across source files recognized by _EXT_TO_LANG.

    This counts physical lines; it does not attempt to filter comments/blank lines.
    """
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in _IGNORE_DIRS]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in _EXT_TO_LANG:
                continue
            fp = os.path.join(root, fname)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    for _ in f:
                        total += 1
            except OSError:
                continue
    return total


def _github_language_bytes(full_name: str, token: Optional[str]) -> Optional[Dict[str, int]]:
    if requests is None:
        return None
    try:
        url = f"https://api.github.com/repos/{full_name}/languages"
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                # Convert keys to our language labels where possible
                return {k: int(v) for k, v in data.items()}
    except Exception:
        return None
    return None


def language_breakdown(path: str, repo_ref: str) -> List[Tuple[str, float]]:
    """Return a sorted list of (language, percent)."""
    # Prefer GitHub API if we can parse owner/repo
    gh_full = parse_github_full_name(repo_ref)
    token = os.getenv("GITHUB_TOKEN")
    totals: Optional[Dict[str, int]] = None
    if gh_full:
        totals = _github_language_bytes(gh_full, token)

    if not totals:
        totals = _local_language_bytes(path)

    total_bytes = sum(totals.values()) if totals else 0
    if total_bytes == 0:
        return []
    items = [(lang, (bytes_count / total_bytes) * 100.0) for lang, bytes_count in totals.items()]
    items.sort(key=lambda x: x[1], reverse=True)
    return [(lang, round(pct, 1)) for lang, pct in items]


def fetch_open_issues(repo_ref: str) -> Optional[int]:
    """Fetch open issues count from GitHub. Returns None if unavailable.

    Note: GitHub's open_issues_count includes PRs; still useful as a signal.
    """
    if requests is None:
        return None
    gh_full = parse_github_full_name(repo_ref)
    if not gh_full:
        return None
    token = os.getenv("GITHUB_TOKEN")
    try:
        url = f"https://api.github.com/repos/{gh_full}"
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and "open_issues_count" in data:
                return int(data["open_issues_count"])  # includes PRs
    except Exception:
        return None
    return None


