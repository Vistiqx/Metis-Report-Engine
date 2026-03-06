"""Tests for API routes."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check_returns_ok(self):
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "Metis Report Engine"
        assert "version" in data


class TestValidateDSL:
    """Test DSL validation endpoint."""
    
    def test_valid_dsl_passes(self):
        dsl = """```report
id: RPT-001
title: Test Report
```"""
        response = client.post("/validate-dsl", json={"dsl_text": dsl})
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
    
    def test_empty_dsl_fails(self):
        response = client.post("/validate-dsl", json={"dsl_text": ""})
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "error" in data


class TestCompileDSL:
    """Test DSL compilation endpoint."""
    
    def test_compile_valid_dsl(self):
        dsl = """```report
id: RPT-001
title: Test Report
```

```finding
id: F-001
title: Test Finding
severity: High
```"""
        response = client.post("/compile-dsl", json={"dsl_text": dsl})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "report" in data
    
    def test_compile_empty_dsl_fails(self):
        response = client.post("/compile-dsl", json={"dsl_text": ""})
        
        assert response.status_code == 400


class TestValidateReportJSON:
    """Test report JSON validation endpoint."""
    
    def test_valid_report_passes(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test", "type": "test"},
            "findings": [
                {
                    "id": "F-001",
                    "title": "Test",
                    "domain": "test",
                    "category": "test",
                    "severity": "High",
                    "summary": "Test",
                }
            ],
            "evidence": [],
            "recommendations": [],
        }
        response = client.post("/validate-report-json", json=report)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
    
    def test_invalid_report_fails(self):
        report = {"report": {"id": "RPT-001"}}  # Missing required sections
        response = client.post("/validate-report-json", json=report)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "error" in data


class TestCompileReportJSON:
    """Test report JSON compilation endpoint."""
    
    def test_compile_partial_report(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test"},
            "findings": [{"title": "Test Finding"}],
            "evidence": [],
            "recommendations": [],
        }
        response = client.post("/compile-report-json", json=report)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "report" in data
        # Should normalize findings
        assert data["report"]["findings"][0]["id"] == "F-001"


class TestRenderHTML:
    """Test HTML rendering endpoint."""
    
    def test_render_html(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test Report"},
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        response = client.post("/render-html", json=report)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert "Test Report" in response.text


class TestRenderPDF:
    """Test PDF rendering endpoint."""
    
    @pytest.mark.skip(reason="PDF generation requires Playwright browser")
    def test_render_pdf(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test Report"},
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        response = client.post("/render-pdf", json=report)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "pdf_path" in data
        assert "pdf_size" in data


class TestGenerateReport:
    """Test legacy generate report endpoint."""
    
    def test_generate_nonexistent_file(self):
        response = client.post("/generate-report", params={"report_path": "/nonexistent/file.json"})
        
        assert response.status_code == 404
