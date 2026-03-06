"""Tests for report linter module."""

import pytest
from engine.lint.report_linter import lint_report, _issue


class TestLintReport:
    """Test report linting functionality."""
    
    def test_no_issues_for_complete_report(self):
        report = {
            "executive_summary": {"overall_risk_rating": "High"},
            "findings": [
                {
                    "id": "F-001",
                    "severity": "Critical",
                    "evidence_refs": ["E-001"],
                    "recommendation_refs": ["REC-001"],
                }
            ],
            "visualizations": [{"id": "V-001", "type": "test"}],
        }
        issues = lint_report(report)
        
        # Should have no errors, maybe some warnings
        errors = [i for i in issues if i["level"] == "error"]
        assert len(errors) == 0
    
    def test_warning_for_missing_executive_summary(self):
        report = {"findings": [{"id": "F-001", "severity": "High"}]}
        issues = lint_report(report)
        
        warning = [i for i in issues if i["code"] == "missing_executive_summary"]
        assert len(warning) == 1
        assert warning[0]["level"] == "warning"
    
    def test_error_for_missing_findings(self):
        report = {"executive_summary": {}}
        issues = lint_report(report)
        
        error = [i for i in issues if i["code"] == "missing_findings"]
        assert len(error) == 1
        assert error[0]["level"] == "error"
    
    def test_error_for_empty_findings(self):
        report = {"findings": []}
        issues = lint_report(report)
        
        error = [i for i in issues if i["code"] == "missing_findings"]
        assert len(error) == 1
    
    def test_warning_for_missing_visualizations(self):
        report = {
            "executive_summary": {},
            "findings": [{"id": "F-001", "severity": "High"}],
        }
        issues = lint_report(report)
        
        warning = [i for i in issues if i["code"] == "missing_visualizations"]
        assert len(warning) == 1
    
    def test_error_for_finding_missing_severity(self):
        report = {
            "findings": [{"id": "F-001"}],  # No severity
        }
        issues = lint_report(report)
        
        error = [i for i in issues if i["code"] == "missing_severity"]
        assert len(error) == 1
        assert "F-001" in error[0]["message"]
    
    def test_warning_for_finding_missing_recommendations(self):
        report = {
            "findings": [{"id": "F-001", "severity": "High"}],
        }
        issues = lint_report(report)
        
        warning = [i for i in issues if i["code"] == "missing_recommendations"]
        assert len(warning) == 1
        assert "F-001" in warning[0]["message"]
    
    def test_warning_for_finding_missing_evidence(self):
        report = {
            "findings": [{"id": "F-001", "severity": "High"}],
        }
        issues = lint_report(report)
        
        warning = [i for i in issues if i["code"] == "missing_evidence"]
        assert len(warning) == 1
        assert "F-001" in warning[0]["message"]
    
    def test_multiple_findings_issues(self):
        report = {
            "findings": [
                {"id": "F-001", "severity": "High"},
                {"id": "F-002"},  # Missing severity
                {"id": "F-003", "severity": "Low"},
            ],
        }
        issues = lint_report(report)
        
        severity_errors = [i for i in issues if i["code"] == "missing_severity"]
        assert len(severity_errors) == 1
        assert "F-002" in severity_errors[0]["message"]
        
        # Should still warn about missing evidence/recs for all findings
        evidence_warnings = [i for i in issues if i["code"] == "missing_evidence"]
        assert len(evidence_warnings) == 3


class TestIssue:
    """Test issue helper function."""
    
    def test_creates_issue_with_all_fields(self):
        issue = _issue("error", "TEST_CODE", "Test message")
        
        assert issue["level"] == "error"
        assert issue["code"] == "TEST_CODE"
        assert issue["message"] == "Test message"
    
    def test_creates_warning_issue(self):
        issue = _issue("warning", "WARN_CODE", "Warning message")
        
        assert issue["level"] == "warning"
        assert issue["code"] == "WARN_CODE"
        assert issue["message"] == "Warning message"
