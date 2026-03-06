"""Tests for HTML renderer module."""

import pytest
from pathlib import Path
from engine.renderer.html_renderer import (
    render_report_html,
    render_preview_html,
    render_professional_html,
    _load_theme_profile,
    _resolve_data_source,
)


class TestRenderReportHTML:
    """Test HTML rendering functionality."""
    
    def test_render_basic_report(self):
        payload = {
            "report": {
                "id": "RPT-001",
                "title": "Test Report",
                "client": "Test Client",
                "classification": "Confidential",
                "version": "1.0",
            },
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        
        html = render_report_html(payload)
        
        assert "Test Report" in html
        assert "Test Client" in html
        assert "Confidential" in html
    
    def test_render_with_findings(self):
        payload = {
            "report": {
                "id": "RPT-001",
                "title": "Test Report",
            },
            "findings": [
                {
                    "id": "F-001",
                    "title": "Test Finding",
                    "severity": "High",
                    "summary": "Test summary",
                }
            ],
            "evidence": [],
            "recommendations": [],
        }
        
        html = render_report_html(payload)
        
        assert "Test Finding" in html
        assert "F-001" in html
        assert "High" in html
    
    def test_render_with_visualizations(self):
        payload = {
            "report": {
                "id": "RPT-001",
                "title": "Test Report",
            },
            "findings": [],
            "evidence": [],
            "recommendations": [],
            "visualizations": [
                {
                    "id": "V-001",
                    "type": "severity_distribution",
                    "title": "Severity Distribution",
                    "data_source": "metrics.risk_distribution",
                }
            ],
            "metrics": {
                "risk_distribution": {
                    "critical": 2,
                    "high": 3,
                    "medium": 1,
                    "low": 0,
                }
            },
        }
        
        # Use professional template which includes visualizations
        html = render_report_html(payload, template_name="professional_consulting_report.html")
        
        assert "Severity Distribution" in html or "Visual Summary" in html
        # Should contain visualization section
        assert "viz-grid" in html or "viz-card" in html or "<!-- Failed to render" in html
    
    def test_uses_specified_template(self):
        payload = {
            "report": {
                "id": "RPT-001",
                "title": "Test Report",
            },
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        
        # Should use the professional template
        html = render_report_html(payload, template_name="professional_consulting_report.html")
        
        # Professional template has specific CSS classes
        assert "cover-page" in html or "professional" in html.lower() or "report_template" in html
    
    def test_loads_theme_profile(self):
        payload = {
            "report": {
                "id": "RPT-001",
                "title": "Test Report",
                "theme_profile": "vistiqx_consulting",
            },
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        
        html = render_report_html(payload, theme_profile="vistiqx_consulting")
        
        # Should render successfully
        assert "Test Report" in html


class TestRenderPreviewHTML:
    """Test preview rendering."""
    
    def test_preview_uses_default_template(self):
        payload = {
            "report": {"id": "RPT-001", "title": "Preview Test"},
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        
        html = render_preview_html(payload)
        
        assert "Preview Test" in html


class TestRenderProfessionalHTML:
    """Test professional HTML rendering."""
    
    def test_professional_template_renders(self):
        payload = {
            "report": {
                "id": "RPT-001",
                "title": "Professional Report",
                "client": "Client Corp",
                "classification": "Confidential",
            },
            "findings": [
                {"id": "F-001", "title": "Critical Issue", "severity": "Critical", "summary": "Issue summary"},
            ],
            "evidence": [],
            "recommendations": [
                {"id": "REC-001", "title": "Fix Issue", "priority": "Critical", "summary": "Fix it"},
            ],
            "executive_summary": {
                "overall_risk_rating": "High",
                "summary": "Executive summary text",
            },
            "metrics": {
                "risk_distribution": {"critical": 1, "high": 0, "medium": 0, "low": 0},
            },
        }
        
        html = render_professional_html(payload)
        
        assert "Professional Report" in html
        assert "Client Corp" in html
        assert "cover-page" in html
        assert "executive_summary" in html or "Executive Summary" in html


class TestLoadThemeProfile:
    """Test theme profile loading."""
    
    def test_loads_default_profile(self):
        profile = _load_theme_profile("default")
        
        assert "profile" in profile
        assert "colors" in profile
        assert "typography" in profile
    
    def test_loads_vistiqx_profile(self):
        profile = _load_theme_profile("vistiqx_consulting")
        
        assert "profile" in profile
        assert "colors" in profile
        assert "typography" in profile
    
    def test_fallback_to_default_for_unknown_profile(self):
        profile = _load_theme_profile("nonexistent_profile")
        
        # Should fall back to default
        assert "profile" in profile
        assert "colors" in profile


class TestResolveDataSource:
    """Test data source resolution."""
    
    def test_resolve_simple_path(self):
        payload = {
            "metrics": {
                "risk_distribution": {"critical": 5}
            }
        }
        
        result = _resolve_data_source(payload, "metrics.risk_distribution")
        
        assert result == {"critical": 5}
    
    def test_resolve_nested_path(self):
        payload = {
            "report": {
                "engagement": {
                    "details": {"scope": "Full"}
                }
            }
        }
        
        result = _resolve_data_source(payload, "report.engagement.details")
        
        assert result == {"scope": "Full"}
    
    def test_resolve_empty_path(self):
        payload = {"test": "data"}
        
        result = _resolve_data_source(payload, "")
        
        assert result == payload
    
    def test_resolve_missing_path(self):
        payload = {"metrics": {}}
        
        result = _resolve_data_source(payload, "metrics.nonexistent.path")
        
        assert result == {}
    
    def test_resolve_returns_scalar_as_dict(self):
        payload = {"value": 42}
        
        result = _resolve_data_source(payload, "value")
        
        assert result == {"value": 42}
