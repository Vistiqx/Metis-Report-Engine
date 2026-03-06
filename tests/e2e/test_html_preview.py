"""E2E tests for HTML preview rendering using Playwright."""

import pytest
import requests


class TestHTMLPreview:
    """Test HTML preview rendering with Playwright."""
    
    def test_preview_loads_without_errors(self, dev_server, page, console_logs, page_errors):
        """Generate report and load preview - verify no console errors."""
        # Create a report via API
        report = {
            "report": {"id": "RPT-E2E-001", "title": "E2E Test Report"},
            "findings": [
                {"id": "F-001", "title": "Test Finding", "severity": "High", "summary": "Test summary"}
            ],
            "evidence": [],
            "recommendations": [],
        }
        
        # Get HTML via API
        response = requests.post(f"{dev_server}/render-html", json=report)
        assert response.status_code == 200
        html = response.text
        
        # Load HTML in browser
        page.set_content(html)
        
        # Verify page loaded
        assert "E2E Test Report" in page.content()
        
        # Check for console errors
        error_logs = [log for log in console_logs if log["type"] == "error"]
        assert len(error_logs) == 0, f"Console errors found: {error_logs}"
        
        # Check for page errors
        assert len(page_errors) == 0, f"Page errors found: {page_errors}"
    
    def test_consulting_template_renders(self, dev_server, page):
        """Verify consulting template displays correctly."""
        report = {
            "report": {
                "id": "RPT-E2E-002",
                "title": "Consulting Template Test",
                "client": "Test Client",
                "classification": "Confidential",
            },
            "executive_summary": {"overall_risk_rating": "High", "summary": "Test summary"},
            "findings": [
                {"id": "F-001", "title": "Critical Finding", "severity": "Critical", "summary": "Critical issue"}
            ],
            "evidence": [],
            "recommendations": [],
            "metrics": {"risk_distribution": {"critical": 1, "high": 0, "medium": 0, "low": 0}},
        }
        
        # Render with professional template
        response = requests.post(
            f"{dev_server}/render-html",
            json=report,
            params={"template": "professional"}
        )
        assert response.status_code == 200
        
        # Load in browser
        page.set_content(response.text)
        
        # Verify consulting template elements
        content = page.content()
        assert "cover-page" in content or "professional" in content.lower()
        assert "Test Client" in content
        assert "Confidential" in content
        assert "Executive Summary" in content or "executive_summary" in content
        assert "Critical Finding" in content
    
    def test_charts_appear_in_preview(self, dev_server, page):
        """Verify SVG charts render correctly."""
        report = {
            "report": {"id": "RPT-E2E-003", "title": "Chart Test"},
            "metrics": {
                "risk_distribution": {
                    "critical": 2,
                    "high": 3,
                    "medium": 1,
                    "low": 0,
                }
            },
            "findings": [
                {"id": "F-001", "title": "Finding 1", "severity": "Critical"},
                {"id": "F-002", "title": "Finding 2", "severity": "High"},
            ],
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
        }
        
        response = requests.post(f"{dev_server}/render-html", json=report)
        assert response.status_code == 200
        
        page.set_content(response.text)
        
        # Check for SVG elements
        svg_elements = page.query_selector_all("svg")
        assert len(svg_elements) > 0, "No SVG charts found in rendered HTML"
    
    def test_responsive_layout(self, dev_server, page):
        """Verify layout at different viewports."""
        report = {
            "report": {"id": "RPT-E2E-004", "title": "Responsive Test"},
            "findings": [{"id": "F-001", "title": "Test", "severity": "High"}],
            "evidence": [],
            "recommendations": [],
        }
        
        response = requests.post(f"{dev_server}/render-html", json=report)
        html = response.text
        
        # Test desktop viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.set_content(html)
        desktop_content = page.content()
        assert "Responsive Test" in desktop_content
        
        # Test tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})
        page.reload()
        tablet_content = page.content()
        assert "Responsive Test" in tablet_content
        
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.reload()
        mobile_content = page.content()
        assert "Responsive Test" in mobile_content


class TestPDFGeneration:
    """Test PDF generation flow end-to-end."""
    
    def test_dsl_to_pdf_pipeline(self, dev_server, page):
        """Full pipeline: DSL -> Compile -> HTML -> PDF."""
        # Step 1: Submit DSL to compile
        dsl = """```report
id: RPT-E2E-PDF
title: PDF Pipeline Test
```

```finding
id: F-001
title: PDF Test Finding
severity: High
```"""
        
        compile_response = requests.post(
            f"{dev_server}/compile-dsl",
            json={"dsl_text": dsl}
        )
        assert compile_response.status_code == 200
        compiled = compile_response.json()["report"]
        
        # Step 2: Generate PDF
        pdf_response = requests.post(
            f"{dev_server}/render-pdf",
            json=compiled,
            params={"skip_quality_gates": "true"}
        )
        
        # If quality gates fail, we should get a 400 with details
        if pdf_response.status_code == 400:
            detail = pdf_response.json().get("detail", {})
            if detail.get("status") == "blocked":
                # Try with skip flag
                pdf_response = requests.post(
                    f"{dev_server}/render-pdf",
                    json=compiled,
                    params={"skip_quality_gates": "true"}
                )
        
        assert pdf_response.status_code == 200
        result = pdf_response.json()
        
        # Verify PDF was created
        assert "pdf_path" in result
        assert "pdf_size" in result
        assert result["pdf_size"] > 0
    
    def test_pdf_quality_gates_block(self, dev_server):
        """Verify PDF generation is blocked by quality gates."""
        # Report with no findings - should fail quality gates
        bad_report = {
            "report": {"id": "RPT-BAD", "title": "Bad Report"},
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        
        response = requests.post(f"{dev_server}/render-pdf", json=bad_report)
        
        # Should be blocked
        assert response.status_code == 400
        detail = response.json().get("detail", {})
        assert detail.get("status") == "blocked"
        assert "quality_gates" in detail
    
    def test_pdf_with_quality_override(self, dev_server):
        """Verify skip_quality_gates parameter works."""
        bad_report = {
            "report": {"id": "RPT-BAD", "title": "Bad Report"},
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        
        # With override, should succeed
        response = requests.post(
            f"{dev_server}/render-pdf",
            json=bad_report,
            params={"skip_quality_gates": "true"}
        )
        
        # Should succeed despite quality issues
        assert response.status_code == 200
        result = response.json()
        assert "pdf_path" in result


class TestDevServerDiagnostics:
    """Test using Chrome DevTools Protocol features."""
    
    def test_no_memory_leaks(self, dev_server, page):
        """Check for memory leaks in preview rendering."""
        report = {
            "report": {"id": "RPT-MEM-001", "title": "Memory Test"},
            "findings": [{"id": "F-001", "title": "Test", "severity": "High"}],
            "evidence": [],
            "recommendations": [],
        }
        
        # Get initial memory
        initial_metrics = page.evaluate("() => performance.memory")
        
        # Render multiple times
        for _ in range(5):
            response = requests.post(f"{dev_server}/render-html", json=report)
            page.set_content(response.text)
            page.reload()
        
        # Get final memory
        final_metrics = page.evaluate("() => performance.memory")
        
        # Memory should not grow unbounded (allow 50% growth)
        if initial_metrics and final_metrics:
            initial_used = initial_metrics.get("usedJSHeapSize", 0)
            final_used = final_metrics.get("usedJSHeapSize", 0)
            if initial_used > 0:
                growth_ratio = final_used / initial_used
                assert growth_ratio < 1.5, f"Memory grew by {growth_ratio:.2f}x, possible leak"
    
    def test_performance_metrics(self, dev_server, page):
        """Capture performance metrics for rendering."""
        report = {
            "report": {"id": "RPT-PERF-001", "title": "Performance Test"},
            "findings": [{"id": "F-001", "title": "Test", "severity": "High"}],
            "evidence": [],
            "recommendations": [],
        }
        
        # Clear performance entries
        page.evaluate("() => performance.clearEntries()")
        
        # Render
        response = requests.post(f"{dev_server}/render-html", json=report)
        page.set_content(response.text)
        
        # Get performance metrics
        metrics = page.evaluate("""() => {
            return {
                loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime,
                firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
            }
        }
        """)
        
        # Basic performance checks
        assert metrics["loadTime"] > 0
        assert metrics["domContentLoaded"] > 0
        # Page should load in reasonable time (under 5 seconds)
        assert metrics["loadTime"] < 5000, f"Page load took {metrics['loadTime']}ms"
