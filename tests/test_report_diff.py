"""Tests for report diff engine."""

import pytest
from engine.analysis.report_diff import (
    diff_reports,
    _compare_finding_content,
    _classify_changes,
    generate_diff_report,
)


class TestDiffReports:
    """Test main diff_reports function."""
    
    def test_no_changes_between_identical_reports(self):
        report = {
            "report": {"id": "RPT-001"},
            "findings": [
                {"id": "F-001", "title": "Test", "severity": "High"},
            ],
        }
        
        result = diff_reports(report, report)
        
        assert result["added_findings"] == []
        assert result["removed_findings"] == []
        assert result["severity_changes"] == []
        assert result["total_changes"] == 0
        assert result["change_classification"] == "none"
        assert "No changes" in result["summary"]
    
    def test_detects_added_findings(self):
        old = {
            "findings": [
                {"id": "F-001", "title": "Original", "severity": "High"},
            ]
        }
        new = {
            "findings": [
                {"id": "F-001", "title": "Original", "severity": "High"},
                {"id": "F-002", "title": "New Finding", "severity": "Medium"},
            ]
        }
        
        result = diff_reports(old, new)
        
        assert "F-002" in result["added_findings"]
        assert len(result["added_findings"]) == 1
        assert result["total_changes"] == 1
    
    def test_detects_removed_findings(self):
        old = {
            "findings": [
                {"id": "F-001", "title": "To Be Removed", "severity": "High"},
            ]
        }
        new = {
            "findings": []
        }
        
        result = diff_reports(old, new)
        
        assert "F-001" in result["removed_findings"]
        assert len(result["removed_findings"]) == 1
    
    def test_detects_severity_changes(self):
        old = {
            "findings": [
                {"id": "F-001", "title": "Test", "severity": "Medium"},
            ]
        }
        new = {
            "findings": [
                {"id": "F-001", "title": "Test", "severity": "Critical"},
            ]
        }
        
        result = diff_reports(old, new)
        
        assert len(result["severity_changes"]) == 1
        change = result["severity_changes"][0]
        assert change["id"] == "F-001"
        assert change["old_severity"] == "Medium"
        assert change["new_severity"] == "Critical"
    
    def test_detects_content_changes(self):
        old = {
            "findings": [
                {"id": "F-001", "title": "Old Title", "severity": "High", "summary": "Old summary"},
            ]
        }
        new = {
            "findings": [
                {"id": "F-001", "title": "New Title", "severity": "High", "summary": "New summary"},
            ]
        }
        
        result = diff_reports(old, new)
        
        assert len(result["content_changes"]) == 1
        change = result["content_changes"][0]
        assert change["id"] == "F-001"
        assert len(change["changes"]) == 2  # title and summary
    
    def test_detects_recommendation_changes(self):
        old = {
            "findings": [],
            "recommendations": [
                {"id": "REC-001", "title": "Old Rec", "priority": "Medium"},
            ]
        }
        new = {
            "findings": [],
            "recommendations": [
                {"id": "REC-001", "title": "Updated Rec", "priority": "High"},
                {"id": "REC-002", "title": "New Rec", "priority": "Low"},
            ]
        }
        
        result = diff_reports(old, new)
        
        assert len(result["recommendation_changes"]) == 2
        # One modified, one added
    
    def test_detects_evidence_changes(self):
        old = {
            "findings": [],
            "evidence": [
                {"id": "E-001", "title": "Old Evidence", "type": "document"},
            ]
        }
        new = {
            "findings": [],
            "evidence": [
                {"id": "E-002", "title": "New Evidence", "type": "technical"},
            ]
        }
        
        result = diff_reports(old, new)
        
        assert len(result["evidence_changes"]) == 2
        # One removed, one added
    
    def test_detects_metrics_changes(self):
        old = {
            "findings": [],
            "metrics": {
                "risk_distribution": {"critical": 1, "high": 2}
            }
        }
        new = {
            "findings": [],
            "metrics": {
                "risk_distribution": {"critical": 2, "high": 1}
            }
        }
        
        result = diff_reports(old, new)
        
        assert "risk_critical" in result["metrics_changes"]
        assert result["metrics_changes"]["risk_critical"]["delta"] == 1
    
    def test_classification_breaking_for_severity_increase(self):
        old = {
            "findings": [{"id": "F-001", "severity": "Low"}]
        }
        new = {
            "findings": [{"id": "F-001", "severity": "Critical"}]
        }
        
        result = diff_reports(old, new)
        
        assert result["change_classification"] == "breaking"
    
    def test_classification_significant_for_additions(self):
        old = {"findings": []}
        new = {"findings": [{"id": "F-001", "severity": "High"}]}
        
        result = diff_reports(old, new)
        
        assert result["change_classification"] == "significant"
    
    def test_classification_cosmetic_for_content_only(self):
        old = {
            "findings": [{"id": "F-001", "severity": "High", "title": "Old"}]
        }
        new = {
            "findings": [{"id": "F-001", "severity": "High", "title": "New"}]
        }
        
        result = diff_reports(old, new)
        
        # Content changes without severity changes = cosmetic
        assert result["change_classification"] == "cosmetic"
    
    def test_generates_summary(self):
        old = {"findings": [{"id": "F-001", "severity": "Medium"}]}
        new = {
            "findings": [
                {"id": "F-001", "severity": "Critical"},
                {"id": "F-002", "severity": "High"},
            ]
        }
        
        result = diff_reports(old, new)
        
        assert "1 new finding" in result["summary"]
        assert "1 severity change" in result["summary"]
    
    def test_handles_missing_ids(self):
        old = {
            "findings": [
                {"title": "No ID Finding"},  # Missing ID
            ]
        }
        new = {
            "findings": [
                {"title": "No ID Finding"},
                {"id": "F-001", "title": "With ID"},
            ]
        }
        
        result = diff_reports(old, new)
        
        # Should handle gracefully
        assert "F-001" in result["added_findings"]


class TestGenerateDiffReport:
    """Test diff report generation."""
    
    def test_generate_markdown_diff(self):
        diff_result = {
            "added_findings": ["F-001"],
            "removed_findings": [],
            "severity_changes": [],
            "content_changes": [],
            "recommendation_changes": [],
            "evidence_changes": [],
            "metrics_changes": {},
            "summary": "1 new finding added",
            "change_classification": "significant",
            "total_changes": 1,
        }
        
        report = generate_diff_report(diff_result, format="markdown")
        
        assert "# Report Comparison" in report
        assert "SIGNIFICANT" in report
        assert "F-001" in report
        assert "1 new finding" in report
    
    def test_generate_html_diff(self):
        diff_result = {
            "added_findings": ["F-001"],
            "removed_findings": [],
            "severity_changes": [],
            "content_changes": [],
            "recommendation_changes": [],
            "evidence_changes": [],
            "metrics_changes": {},
            "summary": "1 new finding",
            "change_classification": "significant",
            "total_changes": 1,
        }
        
        report = generate_diff_report(diff_result, format="html")
        
        assert "<html>" in report
        assert "SIGNIFICANT" in report
        assert "F-001" in report
    
    def test_unsupported_format_raises_error(self):
        with pytest.raises(ValueError, match="Unsupported format"):
            generate_diff_report({}, format="pdf")


class TestCompareFindingContent:
    """Test finding content comparison."""
    
    def test_detects_title_change(self):
        old = {"id": "F-001", "title": "Old Title", "severity": "High"}
        new = {"id": "F-001", "title": "New Title", "severity": "High"}
        
        changes = _compare_finding_content(old, new)
        
        assert len(changes) == 1
        assert changes[0]["field"] == "title"
        assert changes[0]["old_value"] == "Old Title"
        assert changes[0]["new_value"] == "New Title"
    
    def test_detects_multiple_changes(self):
        old = {"id": "F-001", "title": "Old", "summary": "Old summary", "category": "Security"}
        new = {"id": "F-001", "title": "New", "summary": "New summary", "category": "Privacy"}
        
        changes = _compare_finding_content(old, new)
        
        assert len(changes) == 3
        fields = [c["field"] for c in changes]
        assert "title" in fields
        assert "summary" in fields
        assert "category" in fields
    
    def test_no_changes_when_identical(self):
        finding = {"id": "F-001", "title": "Same", "severity": "High"}
        
        changes = _compare_finding_content(finding, finding)
        
        assert changes == []


class TestClassifyChanges:
    """Test change classification."""
    
    def test_breaking_classification(self):
        diff = {
            "added_findings": [],
            "removed_findings": [],
            "severity_changes": [{"old_severity": "Low", "new_severity": "Critical"}],
            "content_changes": [],
            "recommendation_changes": [],
            "evidence_changes": [],
            "total_changes": 1,
        }
        
        classification = _classify_changes(diff)
        
        assert classification == "breaking"
    
    def test_significant_classification(self):
        diff = {
            "added_findings": ["F-001"],
            "removed_findings": [],
            "severity_changes": [],
            "total_changes": 1,
        }
        
        classification = _classify_changes(diff)
        
        assert classification == "significant"
    
    def test_cosmetic_classification(self):
        diff = {
            "added_findings": [],
            "removed_findings": [],
            "severity_changes": [],
            "content_changes": [{"id": "F-001", "changes": []}],
            "total_changes": 1,
        }
        
        classification = _classify_changes(diff)
        
        assert classification == "cosmetic"
    
    def test_none_classification(self):
        diff = {
            "added_findings": [],
            "removed_findings": [],
            "severity_changes": [],
            "content_changes": [],
            "total_changes": 0,
        }
        
        classification = _classify_changes(diff)
        
        assert classification == "none"
