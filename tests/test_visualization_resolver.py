"""Tests for visualization resolver module."""

import pytest
from engine.compiler.visualization_resolver import resolve_visualizations, has_matrix_inputs


class TestResolveVisualizations:
    """Test visualization resolution."""
    
    def test_creates_severity_distribution_when_metrics_present(self):
        report = {
            "metrics": {
                "risk_distribution": {
                    "critical": 2,
                    "high": 3,
                }
            }
        }
        result = resolve_visualizations(report)
        
        severity_viz = [v for v in result if v["type"] == "severity_distribution"]
        assert len(severity_viz) == 1
        assert severity_viz[0]["id"] == "V-001"
        assert severity_viz[0]["data_source"] == "metrics.risk_distribution"
    
    def test_creates_risk_matrix_when_matrix_present(self):
        report = {
            "risk_model": {
                "matrix": [
                    {"risk_id": "F-001", "likelihood": 4, "impact": 5},
                ]
            }
        }
        result = resolve_visualizations(report)
        
        matrix_viz = [v for v in result if v["type"] == "risk_matrix"]
        assert len(matrix_viz) == 1
        assert matrix_viz[0]["id"] == "V-002"
    
    def test_creates_risk_matrix_from_findings_with_likelihood_impact(self):
        report = {
            "findings": [
                {"id": "F-001", "likelihood": 4, "impact": 5},
            ]
        }
        result = resolve_visualizations(report)
        
        matrix_viz = [v for v in result if v["type"] == "risk_matrix"]
        assert len(matrix_viz) == 1
    
    def test_creates_kpi_cards_when_executive_summary_present(self):
        report = {
            "executive_summary": {"overall_risk_rating": "High"}
        }
        result = resolve_visualizations(report)
        
        kpi_viz = [v for v in result if v["type"] == "kpi_summary_cards"]
        assert len(kpi_viz) == 1
        assert kpi_viz[0]["id"] == "V-003"
    
    def test_creates_timeline_when_recommendations_present(self):
        report = {
            "recommendations": [
                {"id": "REC-001", "title": "Test Rec"},
            ]
        }
        result = resolve_visualizations(report)
        
        timeline_viz = [v for v in result if v["type"] == "timeline"]
        assert len(timeline_viz) == 1
        assert timeline_viz[0]["id"] == "V-004"
    
    def test_returns_empty_list_when_no_data(self):
        report = {}
        result = resolve_visualizations(report)
        
        assert result == []
    
    def test_returns_empty_list_when_only_empty_sections(self):
        report = {
            "metrics": {},
            "risk_model": {},
            "findings": [],
            "executive_summary": {},
            "recommendations": [],
        }
        result = resolve_visualizations(report)
        
        assert result == []
    
    def test_all_visualizations_have_required_fields(self):
        report = {
            "metrics": {"risk_distribution": {"critical": 1}},
            "risk_model": {"matrix": []},
            "findings": [{"likelihood": 3, "impact": 4}],
            "executive_summary": {"overall_risk_rating": "Medium"},
            "recommendations": [{"id": "REC-001"}],
        }
        result = resolve_visualizations(report)
        
        for viz in result:
            assert "id" in viz
            assert "type" in viz
            assert "title" in viz
            assert "data_source" in viz
            assert "style_variant" in viz


class TestHasMatrixInputs:
    """Test matrix input detection."""
    
    def test_true_when_findings_have_likelihood_and_impact(self):
        findings = [
            {"id": "F-001", "likelihood": 4, "impact": 5},
        ]
        assert has_matrix_inputs(findings) is True
    
    def test_false_when_findings_missing_likelihood(self):
        findings = [
            {"id": "F-001", "impact": 5},
        ]
        assert has_matrix_inputs(findings) is False
    
    def test_false_when_findings_missing_impact(self):
        findings = [
            {"id": "F-001", "likelihood": 4},
        ]
        assert has_matrix_inputs(findings) is False
    
    def test_false_for_empty_findings(self):
        assert has_matrix_inputs([]) is False
    
    def test_true_with_multiple_findings(self):
        findings = [
            {"id": "F-001", "title": "Test"},
            {"id": "F-002", "likelihood": 3, "impact": 4},
        ]
        # Should return True if at least one finding has both fields
        assert has_matrix_inputs(findings) is True
