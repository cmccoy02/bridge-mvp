"""Analyzes code duplication using jscpd."""

import subprocess
import json
import os
import tempfile

def analyze_duplication(path: str) -> dict:
    """
    Analyzes code duplication using jscpd and provides a detailed report.

    Args:
        path (str): The path to the directory to analyze.

    Returns:
        dict: A dictionary with the duplication percentage and a list of duplicates.
    """
    report_path = os.path.join(tempfile.gettempdir(), "jscpd-report.json")
    command = [
        "jscpd",
        path,
        "--silent",
        "--reporters",
        "json",
        "--output",
        tempfile.gettempdir(),
        "--reporters-json-name",
        "jscpd-report.json"
    ]

    report = {
        "duplication_percentage": 0.0,
        "duplicated_fragments": []
    }

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        with open(report_path, "r") as f:
            jscpd_report = json.load(f)
        
        report["duplication_percentage"] = jscpd_report.get("statistics", {}).get("total", {}).get("percentage", 0.0)

        for dup in jscpd_report.get("duplicates", []):
            report["duplicated_fragments"].append({
                "fragment": dup.get("fragment"),
                "first_file": f"{dup['firstFile']['name']}:{dup['firstFile']['startLoc']['line']}",
                "second_file": f"{dup['secondFile']['name']}:{dup['secondFile']['startLoc']['line']}",
            })
        
        return report

    except FileNotFoundError:
        print("Warning: jscpd not found. Skipping duplication analysis.")
        print("Please install jscpd: npm install -g jscpd")
        return report
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        print(f"Error running jscpd: {e}")
        return report
    finally:
        if os.path.exists(report_path):
            os.remove(report_path) 