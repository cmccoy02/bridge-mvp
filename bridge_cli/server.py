"""FastAPI server exposing analysis as HTTP endpoints and serving the web UI."""

import os
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from bridge_cli.repo_fetcher import fetch_repo
from bridge_cli.analyzers.complexity import calculate_complexity
from bridge_cli.analyzers.churn import analyze_churn
from bridge_cli.analyzers.duplication import analyze_duplication
from bridge_cli.analyzers.security import analyze_security
from bridge_cli.analyzers.overview import (
    get_repo_name,
    get_age_days_and_total_commits,
    language_breakdown,
    fetch_open_issues,
    total_lines_of_code,
)
from bridge_cli.analyzers.health import analyze_health
from bridge_cli.report import generate_report


app = FastAPI(title="Bridge Analyzer API", version="0.1.0")

# Allow browser access if hosting static separately
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(payload: Dict[str, str]) -> Dict[str, Any]:
    repo_ref = payload.get("repo")
    if not repo_ref:
        raise HTTPException(status_code=400, detail="Missing 'repo' in body")

    try:
        with fetch_repo(repo_ref) as repo_path:
            # Core analyzers
            complexity_metrics = calculate_complexity(repo_path)
            churn_metrics = analyze_churn(repo_path)
            duplication_metrics = analyze_duplication(repo_path)
            security_metrics = analyze_security(repo_path)
            health_metrics = analyze_health(repo_path)

            metrics = {
                "complexity": complexity_metrics,
                "churn": churn_metrics,
                "duplication": duplication_metrics,
                "security": security_metrics,
                "health": health_metrics,
            }

            # Overview
            repo_name = get_repo_name(repo_ref)
            age_days, total_commits = get_age_days_and_total_commits(repo_path)
            lang_pct = language_breakdown(repo_path, repo_ref)
            open_issues = fetch_open_issues(repo_ref)
            loc = total_lines_of_code(repo_path)

            # Full JSON report (detailed)
            json_report = generate_report(repo_name, metrics)

            return {
                "summary": {
                    "name": repo_name,
                    "age_days": age_days,
                    "languages": lang_pct,
                    "open_issues": open_issues,
                    "commits": total_commits,
                    "churn_30d": {
                        "commits": churn_metrics.get("total_commits", 0),
                        "files": churn_metrics.get("total_files_changed", 0),
                        "weekly": churn_metrics.get("weekly_commits", []),
                    },
                    "complexity": {
                        "avg": complexity_metrics.get("average_complexity", 0.0),
                        "p90": complexity_metrics.get("p90_complexity", 0.0),
                    },
                    "size_loc": loc,
                    "health": {
                        "contributors": health_metrics.get("contributors", 0),
                        "bus_factor": health_metrics.get("bus_factor", 0),
                        "releases_per_year": health_metrics.get("release_cadence", {}).get("releases_last_year", 0),
                    },
                },
                "report": json_report,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve the web UI (static) from /web at root
_WEB_DIR = Path(__file__).resolve().parent.parent / "web"
if _WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_WEB_DIR), html=True), name="web")


