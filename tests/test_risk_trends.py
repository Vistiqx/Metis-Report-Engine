"""Tests for risk trend analysis module."""

import pytest
from engine.analysis.risk_trends import (
    build_risk_trend_series,
    analyze_risk_trends,
    calculate_risk_velocity,
)


class TestBuildRiskTrendSeries:
    """Test risk trend series building."""
    
    def test_empty_periods(self):
        result = build_risk_trend_series([])
        assert result["labels"] == []
        assert result["critical"] == []
        assert result["high"] == []
    
    def test_single_period(self):
        periods = [{"label": "2025-01", "critical": 2, "high": 5, "medium": 7, "low": 3}]
        result = build_risk_trend_series(periods)
        
        assert result["labels"] == ["2025-01"]
        assert result["critical"] == [2]
        assert result["high"] == [5]
        assert result["medium"] == [7]
        assert result["low"] == [3]
    
    def test_multiple_periods(self):
        periods = [
            {"label": "2025-01", "critical": 2, "high": 5, "medium": 7, "low": 3},
            {"label": "2025-02", "critical": 1, "high": 6, "medium": 8, "low": 2},
            {"label": "2025-03", "critical": 3, "high": 4, "medium": 6, "low": 4},
        ]
        result = build_risk_trend_series(periods)
        
        assert result["labels"] == ["2025-01", "2025-02", "2025-03"]
        assert result["critical"] == [2, 1, 3]
        assert result["high"] == [5, 6, 4]
        assert result["informational"] == [0, 0, 0]  # Not provided, defaults to 0
    
    def test_missing_severities_default_to_zero(self):
        periods = [{"label": "2025-01", "critical": 2}]
        result = build_risk_trend_series(periods)
        
        assert result["critical"] == [2]
        assert result["high"] == [0]
        assert result["medium"] == [0]
        assert result["low"] == [0]
        assert result["informational"] == [0]


class TestAnalyzeRiskTrends:
    """Test risk trend analysis."""
    
    def test_baseline_analysis_no_previous(self):
        current = {
            "findings": [
                {"id": "F-001", "severity": "Critical"},
                {"id": "F-002", "severity": "High"},
                {"id": "F-003", "severity": "High"},
            ]
        }
        
        result = analyze_risk_trends(current, previous_report=None)
        
        assert result["overall_trend"] == "stable"
        assert result["new_findings"] == []
        assert result["resolved_findings"] == []
        assert "Initial assessment" in result["trend_summary"]
        assert "critical" in result["trend_summary"]
    
    def test_identifies_new_findings(self):
        current = {
            "findings": [
                {"id": "F-001", "severity": "High"},
                {"id": "F-002", "severity": "Medium"},
            ]
        }
        previous = {
            "findings": [
                {"id": "F-001", "severity": "High"},
            ]
        }
        
        result = analyze_risk_trends(current, previous)
        
        assert "F-002" in result["new_findings"]
        assert len(result["new_findings"]) == 1
        assert result["resolved_findings"] == []
    
    def test_identifies_resolved_findings(self):
        current = {
            "findings": [
                {"id": "F-001", "severity": "High"},
            ]
        }
        previous = {
            "findings": [
                {"id": "F-001", "severity": "High"},
                {"id": "F-002", "severity": "Medium"},
            ]
        }
        
        result = analyze_risk_trends(current, previous)
        
        assert "F-002" in result["resolved_findings"]
        assert len(result["resolved_findings"]) == 1
        assert result["new_findings"] == []
    
    def test_detects_severity_changes(self):
        current = {
            "findings": [
                {"id": "F-001", "severity": "Critical"},
            ]
        }
        previous = {
            "findings": [
                {"id": "F-001", "severity": "High"},
            ]
        }
        
        result = analyze_risk_trends(current, previous)
        
        assert "F-001" in result["severity_changes"]
        assert result["severity_changes"]["F-001"]["from"] == "High"
        assert result["severity_changes"]["F-001"]["to"] == "Critical"
    
    def test_calculates_increasing_trend(self):
        current = {
            "findings": [
                {"id": "F-001", "severity": "High"},
                {"id": "F-002", "severity": "High"},
                {"id": "F-003", "severity": "Medium"},
            ]
        }
        previous = {
            "findings": [
                {"id": "F-001", "severity": "High"},
            ]
        }
        
        result = analyze_risk_trends(current, previous)
        
        assert result["overall_trend"] == "increasing"
    
    def test_calculates_decreasing_trend(self):
        current = {
            "findings": [
                {"id": "F-001", "severity": "High"},
            ]
        }
        previous = {
            "findings": [
                {"id": "F-001", "severity": "High"},
                {"id": "F-002", "severity": "High"},
                {"id": "F-003", "severity": "Medium"},
            ]
        }
        
        result = analyze_risk_trends(current, previous)
        
        assert result["overall_trend"] == "decreasing"
    
    def test_calculates_risk_score_delta(self):
        current = {
            "findings": [
                {"id": "F-001", "severity": "High", "risk": {"score": 20}},
                {"id": "F-002", "severity": "Medium", "risk": {"score": 12}},
            ]
        }
        previous = {
            "findings": [
                {"id": "F-001", "severity": "High", "risk": {"score": 20}},
            ]
        }
        
        result = analyze_risk_trends(current, previous)
        
        assert result["risk_score_delta"] == 12  # 32 - 20
    
    def test_generates_summary(self):
        current = {
            "findings": [
                {"id": "F-001", "severity": "Critical"},
                {"id": "F-002", "severity": "High"},
            ]
        }
        previous = {
            "findings": [
                {"id": "F-001", "severity": "High"},  # Severity changed
            ]
        }
        
        result = analyze_risk_trends(current, previous)
        
        assert "new finding" in result["trend_summary"]
        assert "severity change" in result["trend_summary"]


class TestCalculateRiskVelocity:
    """Test risk velocity calculation."""
    
    def test_insufficient_data(self):
        reports = [{"findings": []}]
        result = calculate_risk_velocity(reports)
        
        assert result["trend"] == "insufficient_data"
        assert "Need at least 2 reports" in result["message"]
    
    def test_calculates_velocity(self):
        reports = [
            {
                "report": {"date_created": "2025-01-01"},
                "findings": [
                    {"id": "F-001", "risk": {"score": 20}},
                ]
            },
            {
                "report": {"date_created": "2025-02-01"},
                "findings": [
                    {"id": "F-001", "risk": {"score": 20}},
                    {"id": "F-002", "risk": {"score": 15}},
                ]
            },
            {
                "report": {"date_created": "2025-03-01"},
                "findings": [
                    {"id": "F-001", "risk": {"score": 20}},
                    {"id": "F-002", "risk": {"score": 15}},
                    {"id": "F-003", "risk": {"score": 25}},
                ]
            },
        ]
        
        result = calculate_risk_velocity(reports)
        
        assert result["velocity"] == 20.0  # (60 - 20) / 2
        assert result["total_change"] == 40
        assert result["trend"] == "increasing"
        assert len(result["scores"]) == 3
    
    def test_stable_trend(self):
        reports = [
            {
                "report": {"date_created": "2025-01-01"},
                "findings": [
                    {"id": "F-001", "risk": {"score": 20}},
                ]
            },
            {
                "report": {"date_created": "2025-02-01"},
                "findings": [
                    {"id": "F-001", "risk": {"score": 20}},
                ]
            },
        ]
        
        result = calculate_risk_velocity(reports)
        
        assert result["velocity"] == 0
        assert result["total_change"] == 0
        assert result["trend"] == "stable"
    
    def test_decreasing_trend(self):
        reports = [
            {
                "report": {"date_created": "2025-01-01"},
                "findings": [
                    {"id": "F-001", "risk": {"score": 30}},
                    {"id": "F-002", "risk": {"score": 20}},
                ]
            },
            {
                "report": {"date_created": "2025-02-01"},
                "findings": [
                    {"id": "F-001", "risk": {"score": 30}},
                ]
            },
        ]
        
        result = calculate_risk_velocity(reports)
        
        assert result["total_change"] == -20
        assert result["trend"] == "decreasing"
