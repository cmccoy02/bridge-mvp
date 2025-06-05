"""Generates the final JSON report."""

import json
import datetime

def generate_report(repo_name: str, metrics: dict) -> str:
    """
    Generates a JSON report from the collected metrics.

    Args:
        repo_name (str): The name of the repository.
        metrics (dict): A dictionary containing the analysis results.

    Returns:
        str: A JSON string representing the report.
    """
    churn_metrics = metrics.get("churn", {})
    total_commits = churn_metrics.get("total_commits", 0)
    # Calculate weekly average commits from the last 30 days
    weekly_avg_commits = round((total_commits / 4.28), 2)


    report = {
        "repo_name": repo_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "metrics": {
            "complexity": metrics.get("complexity", 0.0),
            "churn": {
                "weekly_avg_commits": weekly_avg_commits,
                "recent_churned_files": churn_metrics.get("recent_churned_files", []),
            },
            "duplication_percentage": metrics.get("duplication", 0.0),
            "security_issues": metrics.get("security", {"high": 0, "medium": 0, "low": 0}),
        },
    }

    return json.dumps(report, indent=2) 