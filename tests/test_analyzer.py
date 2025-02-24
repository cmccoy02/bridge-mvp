"""Tests for the analyzer module."""

import pytest
from unittest.mock import Mock, patch

from bridge_cli.analyzer import RepoAnalyzer, AnalysisResult


@pytest.fixture
def analyzer():
    """Create a RepoAnalyzer instance with a mock token."""
    return RepoAnalyzer("mock_token")


def test_calculate_score():
    """Test the technical debt score calculation."""
    analyzer = RepoAnalyzer("mock_token")
    metrics = {
        'complexity': 5.0,
        'open_issues': 10,
        'security_issues': 2
    }
    
    score = analyzer.calculate_score(metrics)
    assert 0 <= score <= 100
    
    # Test with high values
    high_metrics = {
        'complexity': 20.0,
        'open_issues': 50,
        'security_issues': 10
    }
    high_score = analyzer.calculate_score(high_metrics)
    assert high_score > score


@patch('bridge_cli.analyzer.radon_cc')
def test_calculate_complexity(mock_radon):
    """Test complexity calculation."""
    analyzer = RepoAnalyzer("mock_token")
    
    # Mock radon's complexity calculation
    mock_block = Mock()
    mock_block.complexity = 5
    mock_radon.cc_visit.return_value = [mock_block]
    
    # Test with a mock file
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "mock code"
        complexity = analyzer.calculate_complexity("/mock/path")
        assert complexity == 5.0


def test_analysis_result_creation():
    """Test AnalysisResult dataclass creation."""
    result = AnalysisResult(
        complexity_score=5.0,
        open_issues=10,
        security_issues=2,
        test_coverage=80.0,
        final_score=65.0,
        details={
            'issues_breakdown': {
                'total': 10,
                'bugs': 5,
                'tech_debt': 3
            }
        }
    )
    
    assert result.complexity_score == 5.0
    assert result.open_issues == 10
    assert result.security_issues == 2
    assert result.test_coverage == 80.0
    assert result.final_score == 65.0
    assert 'issues_breakdown' in result.details 