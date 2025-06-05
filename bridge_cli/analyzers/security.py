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
        dict: A dictionary with counts of high, medium, and low severity issues.
    """
    b_config = bandit_config.BanditConfig()
    b_manager = bandit_manager.BanditManager(b_config, "file")
    b_manager.discover_files([path], recursive=True)
    b_manager.run_tests()

    results = b_manager.get_issue_list(sev_level=bandit_constants.LOW, conf_level=bandit_constants.LOW)

    issue_counts = {
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for issue in results:
        if issue.severity == bandit_constants.HIGH:
            issue_counts["high"] += 1
        elif issue.severity == bandit_constants.MEDIUM:
            issue_counts["medium"] += 1
        elif issue.severity == bandit_constants.LOW:
            issue_counts["low"] += 1

    return issue_counts 