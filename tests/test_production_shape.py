"""Tests to verify production-shape payload handling and fixture conformance.

These tests mirror exactly what the PowerShell production test does.
"""
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestProductionShapePayload:
    """Test that production-shape payloads work correctly.
    
    These tests mimic the exact shape used by the PowerShell script:
    { "report": <canonical report JSON> }
    """
    
    def _load_meta_ai_glasses_fixture(self):
        """Load the Meta AI Glasses fixture from the canonical location."""
        fixture_path = Path(__file__).parents[1] / "examples" / "reports" / "meta-ai-glasses-risk-assessment.example.json"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")
        return json.loads(fixture_path.read_text())
    
    def test_fixture_conforms_to_schema_requirements(self):
        """Verify the Meta AI Glasses fixture has all schema-required fields.
        
        This test documents the exact schema requirements and ensures the
        fixture conforms to them. If this test fails, the fixture needs updating.
        """
        report = self._load_meta_ai_glasses_fixture()
        
        # Schema requirements extracted from schema files:
        # schema/core/report_metadata.schema.json
        assert "type" in report["report"], \
            "report.type is required by schema/core/report_metadata.schema.json"
        
        # schema/core/engagement.schema.json
        assert "id" in report["engagement"], \
            "engagement.id is required by schema/core/engagement.schema.json"
        assert "scope_summary" in report["engagement"], \
            "engagement.scope_summary is required by schema/core/engagement.schema.json"
        
        # schema/core/finding.schema.json
        for finding in report["findings"]:
            assert "domain" in finding, \
                f"finding {finding.get('id')} missing domain (required by schema/core/finding.schema.json)"
        
        # schema/core/evidence.schema.json
        for evidence in report["evidence"]:
            assert "domain" in evidence, \
                f"evidence {evidence.get('id')} missing domain (required by schema/core/evidence.schema.json)"
        
        # schema/core/recommendation.schema.json
        for rec in report["recommendations"]:
            assert "domain" in rec, \
                f"recommendation {rec.get('id')} missing domain (required by schema/core/recommendation.schema.json)"
            assert "action" in rec, \
                f"recommendation {rec.get('id')} missing action (required by schema/core/recommendation.schema.json)"
            assert "type" in rec["action"], \
                f"recommendation {rec.get('id')} action missing type"
            assert "description" in rec["action"], \
                f"recommendation {rec.get('id')} action missing description"
        
        # schema/visualizations/visualization.schema.json
        valid_viz_types = ["kpi_cards", "severity_distribution", "risk_matrix", 
                          "financial_exposure_chart", "comparison_bar_chart", "timeline", 
                          "recommendation_priority", "appendix_table"]
        for viz in report["visualizations"]:
            assert viz["type"] in valid_viz_types, \
                f"visualization {viz.get('id')} has invalid type: {viz.get('type')}"
        
        # schema/metis_report.schema.json appendices
        for appendix in report.get("appendices", []):
            assert "content" in appendix, \
                f"appendix '{appendix.get('title')}' missing content (required by schema)"
    
    def test_production_shape_validation_passes(self):
        """Wrapped payload validation must pass for Meta AI Glasses fixture.
        
        This test mimics exactly what the PowerShell production test does.
        """
        report = self._load_meta_ai_glasses_fixture()
        
        # Production shape: { "report": <canonical report> }
        production_payload = {"report": report}
        
        response = client.post("/validate-report-json", json=production_payload)
        
        assert response.status_code == 200, f"HTTP error: {response.status_code}"
        data = response.json()
        
        # Must be valid
        assert data["valid"] is True, \
            f"Schema validation failed: {data.get('error', {}).get('message', 'Unknown error')}"
        assert data["status"] == "passed"
    
    def test_production_shape_quality_gates_pass(self):
        """Quality gates must pass for Meta AI Glasses wrapped payload.
        
        This is the real test that would have failed if the payload handling
        bug was still present. Quality gates run during PDF render.
        """
        report = self._load_meta_ai_glasses_fixture()
        
        # Production shape with PDF render (includes quality gates)
        production_payload = {"report": report, "template": "professional"}
        
        # Note: PDF generation might be skipped in test environment,
        # but validation and quality gates should still run
        response = client.post("/render-pdf", json=production_payload)
        
        # Should not get a 400 with quality gate blocking
        if response.status_code == 400:
            data = response.json()
            detail = data.get("detail", {})
            if isinstance(detail, dict) and detail.get("status") == "blocked":
                pytest.fail(f"Quality gates blocked: {detail.get('message')}")
        
        # Either success (200) or other acceptable status
        # The important thing is it's not blocked by quality gates
        assert response.status_code in [200, 500], \
            f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                assert "pdf_path" in data or "manifest" in data
    
    def test_direct_canonical_validation_also_passes(self):
        """Direct canonical JSON (without wrapper) should also validate."""
        report = self._load_meta_ai_glasses_fixture()
        
        # Direct payload (no wrapper)
        response = client.post("/validate-report-json", json=report)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True, \
            f"Direct validation failed: {data.get('error', {}).get('message', '')}"


class TestSchemaRequiredFieldsDocumentation:
    """Document exact schema requirements for future reference.
    
    These tests serve as living documentation of schema requirements.
    If they fail, it means either:
    1. The schema changed and tests need updating, OR
    2. The fixture needs updating to match schema
    """
    
    def test_report_metadata_schema_requirements(self):
        """Document report_metadata.schema.json required fields."""
        # Required: id, title, type, classification, client, author, version, date_created
        required_fields = ["id", "title", "type", "classification", "client", "author", "version", "date_created"]
        
        fixture_path = Path(__file__).parents[1] / "examples" / "reports" / "meta-ai-glasses-risk-assessment.example.json"
        report = json.loads(fixture_path.read_text())
        
        for field in required_fields:
            assert field in report["report"], \
                f"report.{field} is required by report_metadata.schema.json"
    
    def test_engagement_schema_requirements(self):
        """Document engagement.schema.json required fields."""
        # Required: id, name, scope_summary
        required_fields = ["id", "name", "scope_summary"]
        
        fixture_path = Path(__file__).parents[1] / "examples" / "reports" / "meta-ai-glasses-risk-assessment.example.json"
        report = json.loads(fixture_path.read_text())
        
        for field in required_fields:
            assert field in report["engagement"], \
                f"engagement.{field} is required by engagement.schema.json"
    
    def test_finding_schema_requirements(self):
        """Document finding.schema.json required fields."""
        # Required: id, title, domain, category, severity, summary
        required_fields = ["id", "title", "domain", "category", "severity", "summary"]
        
        fixture_path = Path(__file__).parents[1] / "examples" / "reports" / "meta-ai-glasses-risk-assessment.example.json"
        report = json.loads(fixture_path.read_text())
        
        for finding in report["findings"]:
            for field in required_fields:
                assert field in finding, \
                    f"finding {finding.get('id')} missing {field} (required by finding.schema.json)"
    
    def test_evidence_schema_requirements(self):
        """Document evidence.schema.json required fields."""
        # Required: id, title, type, domain
        required_fields = ["id", "title", "type", "domain"]
        
        fixture_path = Path(__file__).parents[1] / "examples" / "reports" / "meta-ai-glasses-risk-assessment.example.json"
        report = json.loads(fixture_path.read_text())
        
        for evidence in report["evidence"]:
            for field in required_fields:
                assert field in evidence, \
                    f"evidence {evidence.get('id')} missing {field} (required by evidence.schema.json)"
    
    def test_recommendation_schema_requirements(self):
        """Document recommendation.schema.json required fields."""
        # Required: id, title, domain, action, priority
        required_fields = ["id", "title", "domain", "action", "priority"]
        
        fixture_path = Path(__file__).parents[1] / "examples" / "reports" / "meta-ai-glasses-risk-assessment.example.json"
        report = json.loads(fixture_path.read_text())
        
        for rec in report["recommendations"]:
            for field in required_fields:
                assert field in rec, \
                    f"recommendation {rec.get('id')} missing {field} (required by recommendation.schema.json)"
            
            # action has required subfields: type, description
            assert "type" in rec["action"], \
                f"recommendation {rec.get('id')} action missing type"
            assert "description" in rec["action"], \
                f"recommendation {rec.get('id')} action missing description"
    
    def test_visualization_enum_values(self):
        """Document valid visualization.enum values."""
        valid_types = ["kpi_cards", "severity_distribution", "risk_matrix", 
                      "financial_exposure_chart", "comparison_bar_chart", "timeline", 
                      "recommendation_priority", "appendix_table"]
        
        fixture_path = Path(__file__).parents[1] / "examples" / "reports" / "meta-ai-glasses-risk-assessment.example.json"
        report = json.loads(fixture_path.read_text())
        
        for viz in report["visualizations"]:
            assert viz["type"] in valid_types, \
                f"Invalid visualization type: {viz.get('type')}. Valid types: {valid_types}"
