"""Tests for renderer selection and schema version detection."""

import json
import pytest
from pathlib import Path

from engine.renderer.renderer_selector import (
    detect_schema_version,
    select_renderer,
    should_use_consulting_renderer,
)
from engine.renderer.v2_transformer import transform_v2_to_template_context
from engine.renderer.html_renderer import render_report_html


class TestSchemaVersionDetection:
    """Test schema version detection logic."""
    
    def test_detect_explicit_v2_schema_version(self):
        """Detect schema version 2 from explicit field."""
        report = {
            "schema_version": "2.0",
            "report": {"title": "Test Report"}
        }
        version = detect_schema_version(report)
        assert version == "2"
    
    def test_detect_explicit_v2_without_decimal(self):
        """Detect schema version 2 from integer-like string."""
        report = {
            "schema_version": "2",
            "report": {"title": "Test Report"}
        }
        version = detect_schema_version(report)
        assert version == "2"
    
    def test_detect_v1_from_no_schema_version(self):
        """Default to v1 when no schema_version field."""
        report = {
            "report": {"title": "Test Report"},
            "findings": []
        }
        version = detect_schema_version(report)
        assert version == "1"
    
    def test_infer_v2_from_sections_structure(self):
        """Infer v2 from report.sections structure."""
        report = {
            "report": {
                "title": "Test Report",
                "sections": [
                    {"id": "sec1", "title": "Section 1", "type": "introduction"}
                ]
            }
        }
        version = detect_schema_version(report)
        assert version == "2"
    
    def test_v1_report_without_sections(self):
        """Detect v1 for legacy report without sections."""
        report = {
            "report": {"title": "Test Report"},
            "findings": [{"id": "F-001", "title": "Finding"}],
            "recommendations": []
        }
        version = detect_schema_version(report)
        assert version == "1"


class TestRendererSelection:
    """Test renderer selection based on schema version."""
    
    def test_v2_selects_consulting_renderer(self):
        """V2 reports should use consulting renderer."""
        report = {
            "schema_version": "2.0",
            "report": {"title": "Test Report"}
        }
        config = select_renderer(report)
        
        assert config["schema_version"] == "2"
        assert config["renderer"] == "consulting"
        assert "consulting" in config["template"]
        assert config["theme"] == "vistiqx_consulting"
    
    def test_v1_selects_legacy_renderer(self):
        """V1 reports should use legacy renderer."""
        report = {
            "report": {"title": "Test Report"},
            "findings": []
        }
        config = select_renderer(report)
        
        assert config["schema_version"] == "1"
        assert config["renderer"] == "legacy"
        assert config["template"] == "report_template.html"
        assert config["theme"] == "default"
    
    def test_should_use_consulting_renderer_v2(self):
        """Check consulting renderer selection for v2."""
        report = {"schema_version": "2.0", "report": {}}
        assert should_use_consulting_renderer(report) is True
    
    def test_should_use_consulting_renderer_v1(self):
        """Check that v1 doesn't use consulting renderer."""
        report = {"report": {"title": "Test"}, "findings": []}
        assert should_use_consulting_renderer(report) is False


class TestV2Transformation:
    """Test v2 to template context transformation."""
    
    def test_transform_metadata_structure(self):
        """Transform creates proper metadata structure."""
        report = {
            "report": {
                "metadata": {
                    "id": "RPT-001",
                    "title": "Test Report",
                    "classification": "Confidential",
                    "client": {"name": "Test Client"},
                    "consultant": {"name": "Test Consultant", "firm": "Test Firm"}
                },
                "sections": [],
                "findings": [],
                "recommendations": [],
                "appendices": []
            }
        }
        
        context, _ = transform_v2_to_template_context(report)
        
        assert "report" in context
        assert "metadata" in context["report"]
        assert context["report"]["metadata"]["title"] == "Test Report"
        assert context["report"]["metadata"]["classification"] == "Confidential"
    
    def test_transform_sections_with_blocks(self):
        """Transform sections with various block types."""
        report = {
            "report": {
                "metadata": {"title": "Test"},
                "sections": [
                    {
                        "id": "sec1",
                        "title": "Section 1",
                        "type": "introduction",
                        "blocks": [
                            {"type": "paragraph", "text": "Test paragraph"},
                            {"type": "bullet_list", "items": ["Item 1", "Item 2"]},
                            {"type": "callout", "callout": {"type": "info", "title": "Note", "content": "Important"}}
                        ]
                    }
                ],
                "findings": [],
                "recommendations": [],
                "appendices": []
            }
        }
        
        context, _ = transform_v2_to_template_context(report)
        
        sections = context["report"]["sections"]
        assert len(sections) == 1
        assert sections[0]["title"] == "Section 1"
        assert len(sections[0]["blocks"]) == 3
    
    def test_transform_findings(self):
        """Transform findings to consulting format."""
        report = {
            "report": {
                "metadata": {"title": "Test"},
                "sections": [],
                "findings": [
                    {
                        "id": "F-001",
                        "title": "Critical Finding",
                        "description": "Test description",
                        "severity": "Critical",
                        "category": "Security",
                        "likelihood": 4,
                        "impact": 5,
                        "risk_score": 20
                    }
                ],
                "recommendations": [],
                "appendices": []
            }
        }
        
        context, _ = transform_v2_to_template_context(report)
        
        findings = context["report"]["findings"]
        assert len(findings) == 1
        assert findings[0]["id"] == "F-001"
        assert findings[0]["severity"] == "Critical"
    
    def test_transform_recommendations(self):
        """Transform recommendations to consulting format."""
        report = {
            "report": {
                "metadata": {"title": "Test"},
                "sections": [],
                "findings": [],
                "recommendations": [
                    {
                        "id": "REC-001",
                        "title": "Fix Issue",
                        "description": "Test recommendation",
                        "priority": "High",
                        "timeline": "30 days"
                    }
                ],
                "appendices": []
            }
        }
        
        context, _ = transform_v2_to_template_context(report)
        
        recs = context["report"]["recommendations"]
        assert len(recs) == 1
        assert recs[0]["id"] == "REC-001"
        assert recs[0]["priority"] == "High"


class TestRenderPipeline:
    """Test end-to-end render pipeline."""
    
    def test_v2_report_renders_with_consulting_template(self):
        """V2 report should render with consulting template."""
        report = {
            "schema_version": "2.0",
            "report": {
                "metadata": {
                    "id": "RPT-001",
                    "title": "Test Consulting Report",
                    "classification": "Confidential"
                },
                "sections": [
                    {
                        "id": "intro",
                        "title": "Introduction",
                        "type": "introduction",
                        "blocks": [
                            {"type": "paragraph", "text": "This is a test section."}
                        ]
                    }
                ],
                "findings": [],
                "recommendations": [],
                "appendices": []
            }
        }
        
        html = render_report_html(report)
        
        # Consulting template should have specific elements
        assert "cover-page" in html or "Cover Page" in html or "Test Consulting Report" in html
        # Should contain consulting template structure
        assert len(html) > 1000  # Consulting template is much larger than legacy
    
    def test_v1_report_renders_with_legacy_template(self):
        """V1 report should render with legacy template."""
        report = {
            "report": {
                "id": "RPT-001",
                "title": "Test Legacy Report",
                "client": "Test Client"
            },
            "findings": [],
            "recommendations": []
        }
        
        html = render_report_html(report)
        
        # Legacy template should render successfully
        assert "Test Legacy Report" in html
        assert "Test Client" in html
    
    def test_render_with_comprehensive_v2_sample(self):
        """Test with comprehensive v2 sample file."""
        sample_path = Path(__file__).parents[1] / "examples" / "reports" / "schema_v2_comprehensive.example.json"
        
        if not sample_path.exists():
            pytest.skip("Sample file not found")
        
        with open(sample_path, "r") as f:
            report = json.load(f)
        
        html = render_report_html(report)
        
        # Should render successfully
        assert len(html) > 5000  # Comprehensive report should be substantial
        assert "Comprehensive Risk Assessment" in html or "META AI Glasses" in html
        
        # Should have consulting template structure
        sections = html.count('class="section"')
        assert sections > 0, "Should have section elements"


class TestBackwardCompatibility:
    """Ensure backward compatibility with legacy reports."""
    
    def test_legacy_meta_ai_report_still_works(self):
        """Original Meta AI report should still render."""
        sample_path = Path(__file__).parents[1] / "examples" / "reports" / "meta-ai-glasses-risk-assessment.example.json"
        
        if not sample_path.exists():
            pytest.skip("Sample file not found")
        
        with open(sample_path, "r") as f:
            report = json.load(f)
        
        html = render_report_html(report)
        
        # Should render successfully
        assert "META AI Glasses" in html or len(html) > 100
    
    def test_explicit_template_override(self):
        """Explicit template should override auto-selection."""
        report = {
            "schema_version": "2.0",
            "report": {
                "metadata": {"title": "Test", "classification": "Internal"},
                "sections": [],
                "findings": [],
                "recommendations": [],
                "appendices": []
            }
        }
        
        # Force legacy template even for v2
        html = render_report_html(report, template_name="report_template.html")
        
        # Should render with legacy template
        assert len(html) > 0


class TestRenderLogging:
    """Test that render pipeline logs appropriately."""
    
    def test_renderer_selection_logged(self, caplog):
        """Verify renderer selection is logged."""
        import logging
        
        report = {
            "schema_version": "2.0",
            "report": {
                "metadata": {"title": "Test", "classification": "Internal"},
                "sections": [],
                "findings": [],
                "recommendations": [],
                "appendices": []
            }
        }
        
        # Set logging level for test
        with caplog.at_level(logging.INFO):
            html = render_report_html(report)
        
        # Should log renderer selection
        log_text = caplog.text
        assert "schema version" in log_text.lower() or "renderer" in log_text.lower()
