"""Tests for export manager module."""

import pytest
import json
import csv
import io
from pathlib import Path
from unittest.mock import patch, MagicMock
from engine.export.export_manager import (
    export_report,
    export_json,
    export_markdown,
    export_html,
    export_csv,
    export_pdf,
    batch_export,
    ExportError,
)


class TestExportReport:
    """Test main export_report function."""
    
    def test_export_json(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test Report"},
            "findings": [],
        }
        
        result = export_report(report, "json")
        
        # Should return valid JSON
        parsed = json.loads(result)
        assert parsed["report"]["id"] == "RPT-001"
    
    def test_export_markdown(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test Report", "client": "Test Client"},
            "executive_summary": {"overall_risk_rating": "High", "summary": "Test summary"},
            "findings": [
                {"id": "F-001", "title": "Test Finding", "severity": "High", "summary": "Finding summary"},
            ],
        }
        
        result = export_report(report, "markdown")
        
        assert "# Test Report" in result
        assert "Test Client" in result
        assert "## Executive Summary" in result
        assert "## Findings" in result
        assert "F-001" in result
        assert "Finding summary" in result
    
    def test_export_html(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test Report"},
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        
        result = export_report(report, "html")
        
        assert "<html" in result
        assert "Test Report" in result
    
    def test_export_csv(self):
        report = {
            "report": {"id": "RPT-001"},
            "findings": [
                {"id": "F-001", "title": "Finding 1", "severity": "High", "category": "Security"},
                {"id": "F-002", "title": "Finding 2", "severity": "Medium", "category": "Privacy"},
            ],
        }
        
        result = export_report(report, "csv")
        
        # Parse CSV
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        
        assert len(rows) == 3  # Header + 2 findings
        assert rows[0][0] == "ID"
        assert rows[1][0] == "F-001"
        assert rows[2][0] == "F-002"
    
    @patch("engine.export.export_manager.render_pdf_from_html")
    @patch("engine.export.export_manager.render_report_html")
    def test_export_pdf(self, mock_render_html, mock_render_pdf):
        mock_render_html.return_value = "<html>Test</html>"
        mock_render_pdf.return_value = None
        
        report = {
            "report": {"id": "RPT-001", "title": "Test Report"},
            "findings": [],
            "evidence": [],
            "recommendations": [],
        }
        
        result = export_report(report, "pdf")
        
        # Should return path to PDF
        assert result.endswith(".pdf")
        mock_render_html.assert_called_once()
        mock_render_pdf.assert_called_once()
    
    def test_export_unsupported_format(self):
        report = {"report": {"id": "RPT-001"}}
        
        with pytest.raises(ValueError, match="Unsupported export format"):
            export_report(report, "docx")
    
    def test_export_case_insensitive(self):
        report = {"report": {"id": "RPT-001"}}
        
        # Should accept uppercase
        result = export_report(report, "JSON")
        assert json.loads(result)["report"]["id"] == "RPT-001"
        
        result = export_report(report, "Markdown")
        assert "# " in result


class TestExportJSON:
    """Test JSON export."""
    
    def test_export_valid_json(self):
        report = {"report": {"id": "RPT-001", "title": "Test"}, "nested": {"key": "value"}}
        
        result = export_json(report)
        
        parsed = json.loads(result)
        assert parsed["report"]["id"] == "RPT-001"
        assert parsed["nested"]["key"] == "value"
    
    def test_export_with_indent(self):
        report = {"report": {"id": "RPT-001"}}
        
        result = export_json(report, indent=4)
        
        # Should have 4-space indentation
        assert "    " in result
    
    def test_export_unicode(self):
        report = {"report": {"title": "Rapport de Test"}}  # French characters
        
        result = export_json(report)
        
        # Should preserve unicode
        assert "Rapport de Test" in result


class TestExportMarkdown:
    """Test Markdown export."""
    
    def test_export_basic_report(self):
        report = {
            "report": {"id": "RPT-001", "title": "Security Assessment"},
        }
        
        result = export_markdown(report)
        
        assert "# Security Assessment" in result
    
    def test_export_with_metadata(self):
        report = {
            "report": {
                "id": "RPT-001",
                "title": "Test Report",
                "client": "Acme Corp",
                "classification": "Confidential",
                "version": "1.0",
                "date_created": "2026-03-06",
            },
        }
        
        result = export_markdown(report)
        
        assert "Acme Corp" in result
        assert "Confidential" in result
        assert "1.0" in result
        assert "2026-03-06" in result
    
    def test_export_with_findings(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test"},
            "findings": [
                {
                    "id": "F-001",
                    "title": "Critical Issue",
                    "severity": "Critical",
                    "category": "Security",
                    "summary": "This is a critical security issue.",
                    "risk": {"score": 25},
                }
            ],
        }
        
        result = export_markdown(report)
        
        assert "## Findings" in result
        assert "### F-001" in result
        assert "Critical Issue" in result
        assert "Critical" in result
        assert "Security" in result
        assert "This is a critical security issue." in result
        assert "25" in result
    
    def test_export_with_recommendations(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test"},
            "recommendations": [
                {
                    "id": "REC-001",
                    "title": "Fix Issue",
                    "priority": "High",
                    "summary": "Apply the security patch.",
                }
            ],
        }
        
        result = export_markdown(report)
        
        assert "## Recommendations" in result
        assert "REC-001" in result
        assert "Fix Issue" in result
        assert "High" in result
        assert "Apply the security patch." in result
    
    def test_export_with_evidence(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test"},
            "evidence": [
                {
                    "id": "E-001",
                    "title": "Scan Results",
                    "type": "technical",
                    "summary": "Vulnerability scan results.",
                }
            ],
        }
        
        result = export_markdown(report)
        
        assert "## Evidence" in result
        assert "E-001" in result
        assert "technical" in result
    
    def test_export_with_risk_summary(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test"},
            "metrics": {
                "risk_distribution": {
                    "critical": 2,
                    "high": 3,
                    "medium": 1,
                    "low": 0,
                }
            },
        }
        
        result = export_markdown(report)
        
        assert "## Risk Summary" in result
        assert "Critical:** 2" in result
        assert "High:** 3" in result


class TestExportCSV:
    """Test CSV export."""
    
    def test_export_empty_findings(self):
        report = {"report": {"id": "RPT-001"}, "findings": []}
        
        result = export_csv(report)
        
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 1  # Header only
        assert rows[0][0] == "ID"
    
    def test_export_findings(self):
        report = {
            "report": {"id": "RPT-001"},
            "findings": [
                {"id": "F-001", "title": "Issue 1", "severity": "High", "category": "Sec", "summary": "Desc 1", "risk": {"score": 20}},
                {"id": "F-002", "title": "Issue 2", "severity": "Medium", "category": "Priv", "summary": "Desc 2"},
            ],
        }
        
        result = export_csv(report)
        
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        
        assert len(rows) == 3
        assert rows[1][0] == "F-001"
        assert rows[1][1] == "Issue 1"
        assert rows[1][2] == "High"
        assert rows[1][5] == "20"
        assert rows[2][2] == "Medium"
    
    def test_csv_escaping(self):
        report = {
            "report": {"id": "RPT-001"},
            "findings": [
                {"id": "F-001", "title": "Issue with, comma", "severity": "High"},
            ],
        }
        
        result = export_csv(report)
        
        # Should handle commas properly
        assert "Issue with, comma" in result


class TestBatchExport:
    """Test batch export to multiple formats."""
    
    def test_batch_export_multiple_formats(self):
        report = {
            "report": {"id": "RPT-001", "title": "Test"},
            "findings": [],
        }
        
        results = batch_export(report, ["json", "markdown", "csv"])
        
        assert "json" in results
        assert "markdown" in results
        assert "csv" in results
        
        # Should be able to parse JSON result
        assert json.loads(results["json"])["report"]["id"] == "RPT-001"
        assert "# Test" in results["markdown"]
        assert "ID" in results["csv"]
    
    def test_batch_export_with_error(self):
        report = {"report": {"id": "RPT-001"}}
        
        results = batch_export(report, ["json", "unsupported"])
        
        assert "json" in results
        assert "unsupported" in results
        assert "ERROR" in results["unsupported"]


class TestExportError:
    """Test error handling."""
    
    def test_export_error_is_exception(self):
        error = ExportError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
