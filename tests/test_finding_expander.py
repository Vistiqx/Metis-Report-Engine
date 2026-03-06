"""Tests for finding expander module."""

import pytest
from engine.compiler.finding_expander import expand_findings, build_fallback_summary


class TestExpandFindings:
    """Test finding expansion functionality."""
    
    def test_calculates_risk_score(self):
        findings = [
            {"id": "F-001", "likelihood": 4, "impact": 5},
        ]
        result = expand_findings(findings)
        
        assert result[0]["risk"]["likelihood"] == 4
        assert result[0]["risk"]["impact"] == 5
        assert result[0]["risk"]["score"] == 20
    
    def test_skips_risk_calc_if_likelihood_missing(self):
        findings = [
            {"id": "F-001", "impact": 5},
        ]
        result = expand_findings(findings)
        
        assert "risk" not in result[0]
    
    def test_skips_risk_calc_if_impact_missing(self):
        findings = [
            {"id": "F-001", "likelihood": 4},
        ]
        result = expand_findings(findings)
        
        assert "risk" not in result[0]
    
    def test_resolves_evidence_refs(self):
        findings = [
            {
                "id": "F-001",
                "evidence_refs": ["E-001", "E-002"],
            }
        ]
        evidence = [
            {"id": "E-001", "title": "Evidence 1"},
            {"id": "E-002", "title": "Evidence 2"},
        ]
        
        result = expand_findings(findings, evidence=evidence)
        
        assert len(result[0]["resolved_evidence"]) == 2
        assert result[0]["resolved_evidence"][0]["id"] == "E-001"
        assert result[0]["resolved_evidence"][1]["id"] == "E-002"
    
    def test_ignores_unresolved_evidence_refs(self):
        findings = [
            {
                "id": "F-001",
                "evidence_refs": ["E-001", "E-999"],  # E-999 doesn't exist
            }
        ]
        evidence = [
            {"id": "E-001", "title": "Evidence 1"},
        ]
        
        result = expand_findings(findings, evidence=evidence)
        
        # Should only include resolved evidence
        assert len(result[0]["resolved_evidence"]) == 1
        assert result[0]["resolved_evidence"][0]["id"] == "E-001"
    
    def test_resolves_recommendation_refs(self):
        findings = [
            {
                "id": "F-001",
                "recommendation_refs": ["REC-001"],
            }
        ]
        recommendations = [
            {"id": "REC-001", "title": "Recommendation 1"},
        ]
        
        result = expand_findings(findings, recommendations=recommendations)
        
        assert len(result[0]["resolved_recommendations"]) == 1
        assert result[0]["resolved_recommendations"][0]["id"] == "REC-001"
    
    def test_builds_fallback_summary(self):
        findings = [
            {"id": "F-001", "title": "Test Finding", "severity": "High"},
        ]
        result = expand_findings(findings)
        
        assert "Test Finding" in result[0]["summary"]
        assert "High" in result[0]["summary"]
    
    def test_preserves_existing_summary(self):
        findings = [
            {"id": "F-001", "title": "Test", "summary": "Custom summary"},
        ]
        result = expand_findings(findings)
        
        assert result[0]["summary"] == "Custom summary"
    
    def test_handles_empty_findings(self):
        result = expand_findings([])
        assert result == []
    
    def test_handles_no_evidence_or_recommendations(self):
        findings = [
            {"id": "F-001", "likelihood": 3, "impact": 4},
        ]
        result = expand_findings(findings)
        
        assert result[0]["risk"]["score"] == 12
        assert result[0]["resolved_evidence"] == []
        assert result[0]["resolved_recommendations"] == []


class TestBuildFallbackSummary:
    """Test fallback summary generation."""
    
    def test_includes_title_and_severity(self):
        finding = {"title": "Security Vulnerability", "severity": "Critical"}
        summary = build_fallback_summary(finding)
        
        assert "Security Vulnerability" in summary
        assert "Critical" in summary
    
    def test_handles_missing_title(self):
        finding = {"severity": "High"}
        summary = build_fallback_summary(finding)
        
        assert "Untitled finding" in summary
    
    def test_handles_missing_severity(self):
        finding = {"title": "Test Finding"}
        summary = build_fallback_summary(finding)
        
        assert "Informational" in summary
    
    def test_uses_default_for_empty_finding(self):
        finding = {}
        summary = build_fallback_summary(finding)
        
        assert "Untitled finding" in summary
        assert "Informational" in summary
