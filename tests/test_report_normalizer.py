"""Tests for report normalizer module."""

import pytest
from engine.compiler.report_normalizer import (
    normalize_report,
    normalize_finding,
    normalize_recommendation,
    normalize_evidence,
    normalize_metrics,
    normalize_severity,
    severity_rank,
    coerce_int,
)


class TestNormalizeSeverity:
    """Test severity normalization."""
    
    def test_normalize_standard_values(self):
        assert normalize_severity("Critical") == "Critical"
        assert normalize_severity("High") == "High"
        assert normalize_severity("Medium") == "Medium"
        assert normalize_severity("Low") == "Low"
        assert normalize_severity("Informational") == "Informational"
    
    def test_normalize_lowercase(self):
        assert normalize_severity("critical") == "Critical"
        assert normalize_severity("high") == "High"
        assert normalize_severity("medium") == "Medium"
        assert normalize_severity("low") == "Low"
    
    def test_normalize_aliases(self):
        assert normalize_severity("info") == "Informational"
        assert normalize_severity("informational") == "Informational"
        assert normalize_severity("moderate") == "Medium"
    
    def test_normalize_none(self):
        assert normalize_severity(None) == "Informational"
    
    def test_normalize_empty(self):
        assert normalize_severity("") == ""
    
    def test_normalize_unknown(self):
        assert normalize_severity("Unknown") == "Unknown"


class TestSeverityRank:
    """Test severity ranking."""
    
    def test_severity_rank_order(self):
        assert severity_rank("Critical") == 0
        assert severity_rank("High") == 1
        assert severity_rank("Medium") == 2
        assert severity_rank("Low") == 3
        assert severity_rank("Informational") == 4
    
    def test_severity_rank_normalized(self):
        assert severity_rank("critical") == 0  # Should normalize first
        assert severity_rank("HIGH") == 1
    
    def test_severity_rank_unknown(self):
        # Unknown severities should sort to the end
        assert severity_rank("Unknown") == 5


class TestCoerceInt:
    """Test integer coercion."""
    
    def test_coerce_valid_integers(self):
        assert coerce_int(5) == 5
        assert coerce_int("5") == 5
        assert coerce_int(0) == 0
        assert coerce_int(-3) == -3
    
    def test_coerce_returns_default_for_none(self):
        assert coerce_int(None, default=0) == 0
        assert coerce_int(None, default=-1) == -1
    
    def test_coerce_returns_default_for_empty_string(self):
        assert coerce_int("", default=0) == 0
    
    def test_coerce_returns_default_for_invalid(self):
        assert coerce_int("not a number", default=0) == 0
        assert coerce_int("abc", default=-1) == -1
    
    def test_coerce_no_default_returns_none(self):
        assert coerce_int("invalid") is None


class TestNormalizeFinding:
    """Test finding normalization."""
    
    def test_adds_default_id(self):
        finding = {"title": "Test Finding"}
        result = normalize_finding(finding, index=1)
        assert result["id"] == "F-001"
    
    def test_preserves_existing_id(self):
        finding = {"id": "F-999", "title": "Test"}
        result = normalize_finding(finding, index=1)
        assert result["id"] == "F-999"
    
    def test_adds_default_title(self):
        finding = {}
        result = normalize_finding(finding, index=5)
        assert result["title"] == "Finding 5"
    
    def test_normalizes_severity(self):
        finding = {"severity": "critical"}
        result = normalize_finding(finding, index=1)
        assert result["severity"] == "Critical"
    
    def test_coerces_likelihood_and_impact(self):
        finding = {"likelihood": "4", "impact": "5"}
        result = normalize_finding(finding, index=1)
        assert result["likelihood"] == 4
        assert result["impact"] == 5
    
    def test_adds_default_lists(self):
        finding = {}
        result = normalize_finding(finding, index=1)
        assert result["evidence_refs"] == []
        assert result["recommendation_refs"] == []
    
    def test_preserves_existing_values(self):
        finding = {
            "id": "F-123",
            "title": "Custom Title",
            "severity": "High",
            "summary": "Custom summary",
            "evidence_refs": ["E-001"],
        }
        result = normalize_finding(finding, index=1)
        assert result["id"] == "F-123"
        assert result["title"] == "Custom Title"
        assert result["severity"] == "High"
        assert result["summary"] == "Custom summary"
        assert result["evidence_refs"] == ["E-001"]


class TestNormalizeRecommendation:
    """Test recommendation normalization."""
    
    def test_adds_default_id(self):
        rec = {"title": "Test Rec"}
        result = normalize_recommendation(rec, index=1)
        assert result["id"] == "REC-001"
    
    def test_normalizes_priority(self):
        rec = {"priority": "critical"}
        result = normalize_recommendation(rec, index=1)
        assert result["priority"] == "Critical"
    
    def test_adds_default_summary(self):
        rec = {}
        result = normalize_recommendation(rec, index=1)
        assert result["summary"] == ""


class TestNormalizeEvidence:
    """Test evidence normalization."""
    
    def test_adds_default_id(self):
        evidence = {"title": "Test Evidence"}
        result = normalize_evidence(evidence, index=1)
        assert result["id"] == "E-001"
    
    def test_adds_default_type(self):
        evidence = {}
        result = normalize_evidence(evidence, index=1)
        assert result["type"] == "document"


class TestNormalizeMetrics:
    """Test metrics normalization."""
    
    def test_creates_risk_distribution_from_findings(self):
        findings = [
            {"severity": "Critical"},
            {"severity": "Critical"},
            {"severity": "High"},
            {"severity": "Medium"},
        ]
        metrics = normalize_metrics({}, findings)
        
        assert metrics["risk_distribution"]["critical"] == 2
        assert metrics["risk_distribution"]["high"] == 1
        assert metrics["risk_distribution"]["medium"] == 1
        assert metrics["risk_distribution"]["low"] == 0
    
    def test_preserves_existing_distribution(self):
        existing = {"risk_distribution": {"critical": 5, "high": 3}}
        findings = [{"severity": "Low"}]
        metrics = normalize_metrics(existing, findings)
        
        # Should preserve existing values, not recalculate
        assert metrics["risk_distribution"]["critical"] == 5
        assert metrics["risk_distribution"]["high"] == 3
    
    def test_handles_empty_findings(self):
        metrics = normalize_metrics({}, [])
        
        assert metrics["risk_distribution"]["critical"] == 0
        assert metrics["risk_distribution"]["high"] == 0
        assert metrics["risk_distribution"]["medium"] == 0
        assert metrics["risk_distribution"]["low"] == 0


class TestNormalizeReport:
    """Test full report normalization."""
    
    def test_adds_required_sections(self):
        report = {}
        result = normalize_report(report)
        
        assert "report" in result
        assert "executive_summary" in result
        assert "findings" in result
        assert "evidence" in result
        assert "recommendations" in result
        assert "metrics" in result
        assert "risk_model" in result
        assert "visualizations" in result
        assert "appendices" in result
    
    def test_normalizes_all_findings(self):
        report = {
            "findings": [
                {"title": "Finding 1"},
                {"title": "Finding 2"},
            ]
        }
        result = normalize_report(report)
        
        assert len(result["findings"]) == 2
        assert result["findings"][0]["id"] == "F-001"
        assert result["findings"][1]["id"] == "F-002"
    
    def test_sorts_findings_by_severity(self):
        report = {
            "findings": [
                {"id": "F-001", "severity": "Low"},
                {"id": "F-002", "severity": "Critical"},
                {"id": "F-003", "severity": "High"},
            ]
        }
        result = normalize_report(report)
        
        assert result["findings"][0]["id"] == "F-002"  # Critical first
        assert result["findings"][1]["id"] == "F-003"  # High second
        assert result["findings"][2]["id"] == "F-001"  # Low last
    
    def test_sorts_recommendations_by_priority(self):
        report = {
            "recommendations": [
                {"id": "REC-001", "priority": "Low"},
                {"id": "REC-002", "priority": "Critical"},
                {"id": "REC-003", "priority": "High"},
            ]
        }
        result = normalize_report(report)
        
        assert result["recommendations"][0]["id"] == "REC-002"  # Critical first
        assert result["recommendations"][1]["id"] == "REC-003"  # High second
        assert result["recommendations"][2]["id"] == "REC-001"  # Low last
    
    def test_preserves_existing_data(self):
        report = {
            "report": {"id": "RPT-001", "title": "Custom Title"},
            "executive_summary": {"overall_risk_rating": "High"},
        }
        result = normalize_report(report)
        
        assert result["report"]["id"] == "RPT-001"
        assert result["report"]["title"] == "Custom Title"
        assert result["executive_summary"]["overall_risk_rating"] == "High"
