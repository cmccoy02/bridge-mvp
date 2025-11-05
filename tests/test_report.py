import json
from bridge_cli.report import generate_report


def test_generate_report_structure():
    metrics = {
        "complexity": {
            "average_complexity": 3.5,
            "top_complex_functions": [
                {"complexity": 10, "location": "a.py:10 - f"}
            ],
        },
        "churn": {
            "total_commits": 9,
            "recent_churned_files": ["a.py", "b.py"],
        },
        "duplication": {
            "duplication_percentage": 7.5,
            "duplicated_fragments": [
                {
                    "fragment": "...",
                    "first_file": "a.py:1",
                    "second_file": "b.py:2",
                }
            ],
        },
        "security": {
            "issues_by_severity": {"high": 1, "medium": 2, "low": 3},
            "detailed_issues": [
                {
                    "file": "a.py",
                    "line": 12,
                    "description": "test",
                    "severity": "high",
                }
            ],
        },
    }

    report_str = generate_report("example-repo", metrics)
    data = json.loads(report_str)

    assert data["repo_name"] == "example-repo"
    assert "timestamp" in data

    m = data["metrics"]
    assert m["complexity"]["average"] == 3.5
    assert isinstance(m["complexity"]["top_complex_functions"], list)

    assert m["churn"]["weekly_avg_commits"] == round(9 / 4.28, 2)
    assert m["churn"]["recent_churned_files"] == ["a.py", "b.py"]

    assert m["duplication"]["percentage"] == 7.5
    assert isinstance(m["duplication"]["duplicated_fragments"], list)

    assert m["security"]["issues_by_severity"]["high"] == 1
    assert isinstance(m["security"]["detailed_issues"], list)


