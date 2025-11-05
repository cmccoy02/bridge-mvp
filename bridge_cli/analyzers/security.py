"""Runs security analysis using Bandit."""

import os
from bandit.core import manager as bandit_manager
from bandit.core import config as bandit_config
from bandit.core import constants as bandit_constants

def analyze_security(path: str) -> dict:
    """
    Analyzes a directory for security issues using Bandit.

    Args:
        path (str): The path to the directory to analyze.

    Returns:
        dict: A dictionary with counts of issues and a detailed list of
              high and medium severity issues.
    """
    b_config = bandit_config.BanditConfig()
    b_manager = bandit_manager.BanditManager(b_config, "file")
    b_manager.discover_files([path], recursive=True)
    b_manager.run_tests()

    results = b_manager.get_issue_list(sev_level=bandit_constants.LOW, conf_level=bandit_constants.LOW)

    report = {
        "issues_by_severity": {
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "detailed_issues": []
    }

    for issue in results:
        severity_label = str(issue.severity).lower()
        if severity_label in report["issues_by_severity"]:
            report["issues_by_severity"][severity_label] += 1

        if issue.severity in [bandit_constants.HIGH, bandit_constants.MEDIUM]:
            report["detailed_issues"].append({
                "file": issue.fname,
                "line": issue.lineno,
                "description": issue.text,
                "severity": severity_label
            })

    return report 