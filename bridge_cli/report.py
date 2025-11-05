"""Generates the final JSON report."""

import json
import datetime

def generate_report(repo_name: str, metrics: dict) -> str:
    """
    Generates a detailed JSON report from the collected metrics.

    Args:
        repo_name (str): The name of the repository.
        metrics (dict): A dictionary containing the detailed analysis results.

    Returns:
        str: A JSON string representing the report.
    """
    churn_metrics = metrics.get("churn", {})
    total_commits = churn_metrics.get("total_commits", 0)
    weekly_avg_commits = round((total_commits / 4.28), 2) if total_commits > 0 else 0

    complexity_metrics = metrics.get("complexity", {})
    duplication_metrics = metrics.get("duplication", {})
    security_metrics = metrics.get("security", {})

    report = {
        "repo_name": repo_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "metrics": {
            "complexity": {
                "average": complexity_metrics.get("average_complexity", 0.0),
                "top_complex_functions": complexity_metrics.get("top_complex_functions", [])
            },
            "churn": {
                "weekly_avg_commits": weekly_avg_commits,
                "recent_churned_files": churn_metrics.get("recent_churned_files", [])
            },
            "duplication": {
                "percentage": duplication_metrics.get("duplication_percentage", 0.0),
                "duplicated_fragments": duplication_metrics.get("duplicated_fragments", [])
            },
            "security": {
                "issues_by_severity": security_metrics.get("issues_by_severity", {}),
                "detailed_issues": security_metrics.get("detailed_issues", [])
            },
        },
    }

    return json.dumps(report, indent=2) 