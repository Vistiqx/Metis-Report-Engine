"""Integration tests for Metis Report Engine end-to-end workflows."""

import pytest
import json
from pathlib import Path
from engine.compiler.compiler_pipeline import compile_report
from engine.parser.schema_validator import validate_report_with_details
from engine.renderer.html_renderer import render_report_html
from engine.scoring.risk_calculator import summarize_risk_distribution


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_dsl_to_html_workflow(self):
        """Test complete workflow: DSL -> Compile -> Validate -> Render HTML"""
        dsl = """```report
id: RPT-E2E-001
report_type: risk_assessment
title: End-to-End Test Report
client: Test Client
classification: Confidential
version: 1.0
```

```executive_summary
overall_risk_rating: High
summary: |
  This is an end-to-end test of the complete report pipeline.
```

```finding
id: F-001
title: Critical Security Issue
domain: security
category: Vulnerability
severity: Critical
likelihood: 5
impact: 5
summary: |
  A critical security vulnerability was discovered.
evidence_refs:
  - E-001
recommendation_refs:
  - REC-001
```

```evidence
id: E-001
title: Vulnerability Scan Results
type: technical
subtype: scan_report
domain: security
```

```recommendation
id: REC-001
title: Patch Critical Vulnerability
priority: Critical
action:
  type: remediation
  description: Apply security patch immediately
```"""
        
        # Step 1: Compile DSL
        compiled = compile_report(dsl_text=dsl)
        
        assert compiled["report"]["id"] == "RPT-E2E-001"
        assert compiled["report"]["title"] == "End-to-End Test Report"
        assert len(compiled["findings"]) == 1
        assert compiled["findings"][0]["risk"]["score"] == 25  # 5 * 5
        
        # Step 2: Validate
        validation = validate_report_with_details(compiled)
        
        # Step 3: Calculate metrics
        compiled["derived_metrics"] = summarize_risk_distribution(compiled)
        assert compiled["derived_metrics"]["critical"] == 1
        
        # Step 4: Render HTML
        html = render_report_html(compiled)
        assert "End-to-End Test Report" in html
        assert "Critical Security Issue" in html
    
    def test_json_normalization_workflow(self):
        """Test workflow: Partial JSON -> Normalize -> Expand -> Render"""
        partial_json = {
            "report": {
                "id": "RPT-E2E-002",
                "title": "Partial Report Test",
            },
            "findings": [
                {"title": "Finding without ID", "severity": "High"},
                {"title": "Another finding", "severity": "Medium"},
            ],
            "recommendations": [
                {"title": "Recommendation without ID", "priority": "High"},
            ],
        }
        
        # Step 1: Compile/Normalize
        compiled = compile_report(report_json=partial_json)
        
        # Check normalization
        assert compiled["findings"][0]["id"] == "F-001"
        assert compiled["findings"][1]["id"] == "F-002"
        assert compiled["recommendations"][0]["id"] == "REC-001"
        
        # Check sorting (Critical/High before Medium)
        assert compiled["findings"][0]["severity"] == "High"
        assert compiled["findings"][1]["severity"] == "Medium"
        
        # Step 2: Render
        html = render_report_html(compiled)
        assert "Partial Report Test" in html
        assert "F-001" in html
        assert "REC-001" in html


class TestExampleReports:
    """Test with example report files."""
    
    def test_example_report_minimal(self):
        """Test that minimal example can be processed."""
        example_path = Path("examples/example_report_minimal.json")
        if not example_path.exists():
            pytest.skip("Example file not found")
        
        with open(example_path) as f:
            report = json.load(f)
        
        # Should be able to compile
        compiled = compile_report(report_json=report)
        
        # Should render
        html = render_report_html(compiled)
        assert len(html) > 0
    
    def test_example_report_full(self):
        """Test that full example can be processed."""
        example_path = Path("examples/example_report.json")
        if not example_path.exists():
            pytest.skip("Example file not found")
        
        with open(example_path) as f:
            report = json.load(f)
        
        # Add required sections if missing
        if "findings" not in report:
            report["findings"] = []
        if "evidence" not in report:
            report["evidence"] = []
        if "recommendations" not in report:
            report["recommendations"] = []
        
        # Should be able to compile
        compiled = compile_report(report_json=report)
        
        # Should render
        html = render_report_html(compiled)
        assert len(html) > 0


class TestReportQuality:
    """Test report quality and completeness."""
    
    def test_complete_report_has_all_sections(self):
        """Verify complete report has all required sections."""
        dsl = """```report
id: RPT-QUALITY-001
title: Quality Test Report
```"""
        
        compiled = compile_report(dsl_text=dsl)
        
        # Check all sections exist
        assert "report" in compiled
        assert "executive_summary" in compiled
        assert "findings" in compiled
        assert "evidence" in compiled
        assert "recommendations" in compiled
        assert "metrics" in compiled
        assert "risk_model" in compiled
        assert "visualizations" in compiled
    
    def test_report_with_visualizations(self):
        """Test report with all visualization types."""
        report = {
            "report": {"id": "RPT-VIZ-001", "title": "Visualization Test"},
            "executive_summary": {"overall_risk_rating": "High"},
            "metrics": {
                "risk_distribution": {
                    "critical": 2,
                    "high": 3,
                    "medium": 1,
                    "low": 0,
                }
            },
            "risk_model": {
                "matrix": [
                    {"risk_id": "R-001", "likelihood": 4, "impact": 5},
                ]
            },
            "findings": [
                {"id": "F-001", "title": "Test", "severity": "High", "likelihood": 4, "impact": 5},
            ],
            "evidence": [],
            "recommendations": [
                {"id": "REC-001", "title": "Test Rec", "priority": "High"},
            ],
        }
        
        compiled = compile_report(report_json=report)
        
        # Should have visualizations
        viz_types = [v["type"] for v in compiled["visualizations"]]
        assert "severity_distribution" in viz_types
        assert "risk_matrix" in viz_types
        assert "kpi_summary_cards" in viz_types
        assert "timeline" in viz_types


class TestDeterministicBehavior:
    """Test that operations are deterministic."""
    
    def test_compilation_is_deterministic(self):
        """Same input should produce same output."""
        dsl = """```report
id: RPT-DET-001
title: Determinism Test
```

```finding
id: F-001
title: Finding A
severity: High
```

```finding
id: F-002
title: Finding B
severity: Critical
```"""
        
        compiled1 = compile_report(dsl_text=dsl)
        compiled2 = compile_report(dsl_text=dsl)
        
        # Should be identical
        assert json.dumps(compiled1, sort_keys=True) == json.dumps(compiled2, sort_keys=True)
        
        # Findings should be in same order (sorted by severity)
        assert compiled1["findings"][0]["id"] == "F-002"  # Critical first
        assert compiled2["findings"][0]["id"] == "F-002"
    
    def test_scoring_is_deterministic(self):
        """Risk calculations should be deterministic."""
        report = {
            "findings": [
                {"id": "F-001", "severity": "High", "risk": {"score": 20}},
                {"id": "F-002", "severity": "Critical", "risk": {"score": 25}},
            ]
        }
        
        dist1 = summarize_risk_distribution(report)
        dist2 = summarize_risk_distribution(report)
        
        assert dist1 == dist2
