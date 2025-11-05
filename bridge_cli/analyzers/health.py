"""Repository health KPIs: contributors, bus factor, release cadence."""

import time
from typing import Dict

try:
    from git import Repo
    from git.exc import InvalidGitRepositoryError, NoSuchPathError
except Exception:  # pragma: no cover
    Repo = None  # type: ignore
    InvalidGitRepositoryError = Exception  # type: ignore
    NoSuchPathError = Exception  # type: ignore


def _bus_factor_from_author_counts(author_counts: Dict[str, int]) -> int:
    total = sum(author_counts.values())
    if total == 0:
        return 0
    running = 0
    factor = 0
    for _, cnt in sorted(author_counts.items(), key=lambda x: x[1], reverse=True):
        running += cnt
        factor += 1
        if running >= total * 0.5:
            return factor
    return factor


def analyze_health(path: str) -> dict:
    if Repo is None:
        return {
            "contributors": 0,
            "bus_factor": 0,
            "top_authors": [],
            "release_cadence": {"avg_days_between_releases": 0.0, "releases_last_year": 0},
        }
    try:
        repo = Repo(path)
    except (InvalidGitRepositoryError, NoSuchPathError):
        return {
            "contributors": 0,
            "bus_factor": 0,
            "top_authors": [],
            "release_cadence": {"avg_days_between_releases": 0.0, "releases_last_year": 0},
        }

    # Authors/Contributors and bus factor
    author_counts: Dict[str, int] = {}
    for c in repo.iter_commits("HEAD"):
        try:
            key = (c.author.email or c.author.name or "unknown").lower()
        except Exception:
            key = "unknown"
        author_counts[key] = author_counts.get(key, 0) + 1
    contributors = len(author_counts)
    bus_factor = _bus_factor_from_author_counts(author_counts)
    top_authors = [
        {"author": a, "commits": n}
        for a, n in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    # Release cadence via tags
    tag_dates = []
    for t in getattr(repo, "tags", []):
        try:
            tag_dates.append(int(t.commit.committed_date))
        except Exception:
            continue
    tag_dates = sorted(tag_dates)
    avg_days = 0.0
    if len(tag_dates) >= 2:
        diffs = []
        for i in range(1, len(tag_dates)):
            diffs.append((tag_dates[i] - tag_dates[i - 1]) / 86400.0)
        avg_days = round(sum(diffs) / len(diffs), 1)
    now = int(time.time())
    one_year_ago = now - 365 * 86400
    releases_last_year = sum(1 for d in tag_dates if d >= one_year_ago)

    return {
        "contributors": contributors,
        "bus_factor": bus_factor,
        "top_authors": top_authors,
        "release_cadence": {
            "avg_days_between_releases": avg_days,
            "releases_last_year": releases_last_year,
        },
    }


