"""Tests for compiler pipeline orchestration."""

import pytest
from engine.compiler.compiler_pipeline import compile_report, CompilerPipelineError


class TestCompileReport:
    """Test full compiler pipeline."""
    
    def test_compile_from_dsl(self):
        dsl_text = """```report
id: RPT-001
title: Test Report
```

```finding
id: F-001
title: Test Finding
severity: High
```"""
        
        result = compile_report(dsl_text=dsl_text)
        
        assert result["report"]["id"] == "RPT-001"
        assert len(result["findings"]) == 1
        assert result["findings"][0]["id"] == "F-001"
    
    def test_compile_from_partial_json(self):
        report_json = {
            "report": {"id": "RPT-002", "title": "Partial Report"},
            "findings": [
                {"title": "Finding without ID"},
            ],
        }
        
        result = compile_report(report_json=report_json)
        
        assert result["report"]["id"] == "RPT-002"
        # Should normalize the finding (add ID, etc.)
        assert result["findings"][0]["id"] == "F-001"
    
    def test_compile_from_complete_json(self):
        report_json = {
            "report": {"id": "RPT-003", "title": "Complete Report"},
            "findings": [
                {"id": "F-001", "title": "Finding 1", "severity": "Critical"},
                {"id": "F-002", "title": "Finding 2", "severity": "Medium"},
            ],
            "evidence": [{"id": "E-001", "title": "Evidence 1"}],
            "recommendations": [{"id": "REC-001", "title": "Rec 1"}],
        }
        
        result = compile_report(report_json=report_json)
        
        # Findings should be expanded
        assert "resolved_evidence" in result["findings"][0]
        
        # Visualizations should be resolved
        assert len(result["visualizations"]) > 0
    
    def test_error_when_both_inputs_provided(self):
        with pytest.raises(CompilerPipelineError, match="either dsl_text or report_json, not both"):
            compile_report(dsl_text="test", report_json={"test": "data"})
    
    def test_error_when_no_input_provided(self):
        with pytest.raises(CompilerPipelineError, match="No report input"):
            compile_report()
    
    def test_preserves_existing_visualizations(self):
        report_json = {
            "report": {"id": "RPT-004"},
            "findings": [],
            "visualizations": [
                {"id": "V-999", "type": "custom", "title": "Custom Viz"},
            ],
        }
        
        result = compile_report(report_json=report_json)
        
        # Should preserve existing visualizations
        custom_viz = [v for v in result["visualizations"] if v["id"] == "V-999"]
        assert len(custom_viz) == 1
    
    def test_expands_findings_with_evidence_and_recommendations(self):
        report_json = {
            "report": {"id": "RPT-005"},
            "findings": [
                {
                    "id": "F-001",
                    "title": "Test Finding",
                    "evidence_refs": ["E-001"],
                    "recommendation_refs": ["REC-001"],
                }
            ],
            "evidence": [{"id": "E-001", "title": "Evidence 1"}],
            "recommendations": [{"id": "REC-001", "title": "Rec 1"}],
        }
        
        result = compile_report(report_json=report_json)
        
        finding = result["findings"][0]
        assert len(finding["resolved_evidence"]) == 1
        assert len(finding["resolved_recommendations"]) == 1
    
    def test_sorts_findings_and_recommendations(self):
        report_json = {
            "report": {"id": "RPT-006"},
            "findings": [
                {"id": "F-001", "severity": "Low"},
                {"id": "F-002", "severity": "Critical"},
            ],
            "recommendations": [
                {"id": "REC-001", "priority": "Medium"},
                {"id": "REC-002", "priority": "High"},
            ],
        }
        
        result = compile_report(report_json=report_json)
        
        # Findings should be sorted by severity
        assert result["findings"][0]["id"] == "F-002"  # Critical
        
        # Recommendations should be sorted by priority
        assert result["recommendations"][0]["id"] == "REC-002"  # High
