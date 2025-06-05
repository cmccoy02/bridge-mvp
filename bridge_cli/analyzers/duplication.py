"""Analyzes code duplication using jscpd."""

import subprocess
import json

def analyze_duplication(path: str) -> float:
    """
    Analyzes code duplication using jscpd.

    Args:
        path (str): The path to the directory to analyze.

    Returns:
        float: The duplication percentage.
    """
    command = [
        "jscpd",
        path,
        "--silent",
        "--reporters",
        "json",
        "--output",
        ".",
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        with open("report.json", "r") as f:
            report = json.load(f)
        return report["statistics"]["total"]["percentage"]
    except FileNotFoundError:
        print("Warning: jscpd not found. Skipping duplication analysis.")
        print("Please install jscpd: npm install -g jscpd")
        return 0.0
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        print(f"Error running jscpd: {e}")
        return 0.0
    finally:
        # Clean up the report file
        if "os" not in globals():
            import os
        if os.path.exists("report.json"):
            os.remove("report.json") 