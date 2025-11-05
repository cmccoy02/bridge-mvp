import os
import tempfile

from bridge_cli.analyzers.churn import analyze_churn


def test_analyze_churn_on_non_git_directory():
    with tempfile.TemporaryDirectory() as d:
        # Create a dummy file so directory is non-empty
        p = os.path.join(d, "foo.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write("hello")

        result = analyze_churn(d, days=7)
        assert result["total_commits"] == 0
        assert result["total_files_changed"] == 0
        assert result["recent_churned_files"] == []


