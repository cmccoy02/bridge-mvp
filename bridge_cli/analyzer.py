"""Core analysis functionality for the Bridge CLI tool."""

import os
import shutil
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

import radon.complexity as radon_cc
from bandit.core import manager as bandit_manager
from bandit.core import config as bandit_config
from github import Github
from github.Repository import Repository

from bridge_cli.utils import clone_repository


@dataclass
class AnalysisResult:
    """Container for repository analysis results."""
    complexity_score: float
    open_issues: int
    security_issues: int
    test_coverage: Optional[float]
    final_score: float
    details: Dict[str, any]
    metadata: Dict[str, any]


class RepoAnalyzer:
    """Analyzes GitHub repositories for technical debt."""
    
    def __init__(self, github_token: str):
        """Initialize with GitHub token."""
        self.github = Github(github_token)
        self._temp_dir = None
        
    def __del__(self):
        """Cleanup temporary directory if it exists."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir)
        
    def clone_repo(self, repo_url: str) -> str:
        """Clone a repository and return its local path."""
        self._temp_dir = clone_repository(repo_url)
        return self._temp_dir
        
    def calculate_complexity(self, repo_path: str) -> float:
        """Calculate average cyclomatic complexity using radon."""
        total_complexity = 0
        file_count = 0
        
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            blocks = radon_cc.cc_visit(content)
                            if blocks:
                                total_complexity += sum(block.complexity for block in blocks)
                                file_count += 1
                    except Exception:
                        continue
                        
        return total_complexity / max(file_count, 1)
        
    def count_issues(self, repo: Repository) -> Dict[str, int]:
        """Count open issues by type."""
        issues = {
            'total': 0,
            'bugs': 0,
            'tech_debt': 0
        }
        
        for issue in repo.get_issues(state='open'):
            issues['total'] += 1
            labels = [label.name.lower() for label in issue.labels]
            if 'bug' in labels:
                issues['bugs'] += 1
            if 'tech-debt' in labels or 'technical debt' in labels:
                issues['tech_debt'] += 1
                
        return issues
        
    def run_security_scan(self, repo_path: str) -> int:
        """Run security scan using bandit."""
        # Initialize bandit with default config
        conf = bandit_config.BanditConfig()
        mgr = bandit_manager.BanditManager(conf, 'file')
        
        # Find Python files
        python_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Run the scan
        mgr.discover_files(python_files)
        mgr.run_tests()
        
        # Count high and medium severity issues
        issues = mgr.get_issue_list()
        high_severity = sum(1 for i in issues if i.severity == 2)  # HIGH
        medium_severity = sum(1 for i in issues if i.severity == 1)  # MEDIUM
        
        return high_severity + medium_severity
        
    def get_repo_metadata(self, repo: Repository) -> Dict[str, any]:
        """Get repository metadata."""
        try:
            # Get the latest commit
            commits = list(repo.get_commits(per_page=1))
            last_commit = commits[0].commit.author.date if commits else None
        except Exception:
            last_commit = None
        
        return {
            'created_at': repo.created_at,
            'last_commit_at': last_commit,
            'primary_language': repo.language
        }
        
    def calculate_score(self, metrics: Dict[str, float]) -> float:
        """Calculate final technical debt score (0-100)."""
        weights = {
            'complexity': 0.5,
            'open_issues': 0.3,
            'security': 0.2
        }
        
        # Normalize each metric to 0-100 scale and apply weights
        score = (
            (min(metrics['complexity'] * 10, 100) * weights['complexity']) +
            (min(metrics['open_issues'] * 5, 100) * weights['open_issues']) +
            (min(metrics['security_issues'] * 20, 100) * weights['security'])
        )
        
        return min(score, 100)
        
    def analyze_repo(self, repo_url: str) -> AnalysisResult:
        """Perform complete analysis of a repository."""
        # Extract repo name from URL
        if '/' not in repo_url:
            raise ValueError("Repository URL must be in format 'owner/repository'")
            
        repo = self.github.get_repo(repo_url)
        
        # Clone repo
        repo_path = self.clone_repo(repo_url)
        
        # Gather metrics
        complexity = self.calculate_complexity(repo_path)
        issues = self.count_issues(repo)
        security_issues = self.run_security_scan(repo_path)
        
        # Get repository metadata
        metadata = self.get_repo_metadata(repo)
        
        # Calculate final score
        metrics = {
            'complexity': complexity,
            'open_issues': issues['total'],
            'security_issues': security_issues
        }
        final_score = self.calculate_score(metrics)
        
        return AnalysisResult(
            complexity_score=complexity,
            open_issues=issues['total'],
            security_issues=security_issues,
            test_coverage=None,  # To be implemented
            final_score=final_score,
            details={
                'issues_breakdown': issues,
                'raw_metrics': metrics
            },
            metadata=metadata
        ) 