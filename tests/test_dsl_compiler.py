"""Tests for DSL compiler module."""

import pytest
from engine.compiler.dsl_compiler import (
    compile_dsl_text,
    parse_dsl_blocks,
    parse_key_value_block,
    coerce_scalar,
    DSLCompilerError,
)


class TestParseDSLBlocks:
    """Test DSL block parsing."""
    
    def test_parse_single_report_block(self):
        dsl = """```report
id: RPT-001
title: Test Report
```"""
        blocks = parse_dsl_blocks(dsl)
        assert len(blocks) == 1
        assert blocks[0].block_type == "report"
        assert "id: RPT-001" in blocks[0].body
    
    def test_parse_multiple_blocks(self):
        dsl = """```report
id: RPT-001
```

```finding
id: F-001
```"""
        blocks = parse_dsl_blocks(dsl)
        assert len(blocks) == 2
        assert blocks[0].block_type == "report"
        assert blocks[1].block_type == "finding"
    
    def test_parse_empty_dsl(self):
        blocks = parse_dsl_blocks("")
        assert len(blocks) == 0
    
    def test_parse_no_blocks(self):
        blocks = parse_dsl_blocks("Just some text without code blocks")
        assert len(blocks) == 0


class TestParseKeyValueBlock:
    """Test key-value block parsing."""
    
    def test_simple_key_value(self):
        body = "id: RPT-001\ntitle: Test Report"
        result = parse_key_value_block(body)
        assert result["id"] == "RPT-001"
        assert result["title"] == "Test Report"
    
    def test_multiline_scalar(self):
        body = """summary: |
  This is a multiline
  summary text."""
        result = parse_key_value_block(body)
        assert "This is a multiline" in result["summary"]
        assert "summary text." in result["summary"]
    
    def test_list_parsing(self):
        body = """evidence_refs:
  - E-001
  - E-002
  - E-003"""
        result = parse_key_value_block(body)
        assert result["evidence_refs"] == ["E-001", "E-002", "E-003"]
    
    def test_empty_list(self):
        body = "tags:"
        result = parse_key_value_block(body)
        assert result["tags"] == []
    
    def test_numeric_coercion(self):
        body = """likelihood: 4
impact: 5
count: 10
enabled: true
ratio: 3.14"""
        result = parse_key_value_block(body)
        assert result["likelihood"] == 4
        assert result["impact"] == 5
        assert result["count"] == 10
        assert result["enabled"] is True
        assert result["ratio"] == 3.14


class TestCoerceScalar:
    """Test scalar value coercion."""
    
    def test_coerce_boolean_true(self):
        assert coerce_scalar("true") is True
        assert coerce_scalar("TRUE") is True
        assert coerce_scalar("True") is True
    
    def test_coerce_boolean_false(self):
        assert coerce_scalar("false") is False
        assert coerce_scalar("FALSE") is False
        assert coerce_scalar("False") is False
    
    def test_coerce_integer(self):
        assert coerce_scalar("42") == 42
        assert coerce_scalar("0") == 0
        assert coerce_scalar("-5") == -5
    
    def test_coerce_float(self):
        assert coerce_scalar("3.14") == 3.14
        assert coerce_scalar("0.5") == 0.5
    
    def test_coerce_string(self):
        assert coerce_scalar("hello") == "hello"
        assert coerce_scalar("test string") == "test string"


class TestCompileDSLText:
    """Test full DSL compilation."""
    
    def test_compile_complete_report(self):
        dsl = """```report
id: RPT-2026-001
report_type: risk_assessment
title: Meta AI Glasses Risk Assessment
client: Signal Security
classification: Confidential
version: 1.0
```

```executive_summary
overall_risk_rating: High
summary: |
  The assessed deployment presents material privacy and legal exposure.
```

```finding
id: F-001
title: Unauthorized Biometric Capture
domain: risk_assessment
category: Privacy
severity: Critical
likelihood: 4
impact: 5
summary: |
  The workflow allows biometric collection without enforceable consent.
evidence_refs:
  - E-001
```

```evidence
id: E-001
title: Illinois BIPA statutory reference
type: document
subtype: legal_reference
```

```recommendation
id: REC-001
title: Disable Biometric Capture by Default
priority: Critical
```"""
        
        result = compile_dsl_text(dsl)
        
        # Verify report structure
        assert result["report"]["id"] == "RPT-2026-001"
        assert result["report"]["title"] == "Meta AI Glasses Risk Assessment"
        
        # Verify executive summary
        assert result["executive_summary"]["overall_risk_rating"] == "High"
        
        # Verify findings
        assert len(result["findings"]) == 1
        finding = result["findings"][0]
        assert finding["id"] == "F-001"
        assert finding["severity"] == "Critical"
        assert finding["risk"]["score"] == 20  # 4 * 5
        
        # Verify evidence
        assert len(result["evidence"]) == 1
        assert result["evidence"][0]["id"] == "E-001"
        
        # Verify recommendations
        assert len(result["recommendations"]) == 1
        assert result["recommendations"][0]["id"] == "REC-001"
    
    def test_compile_empty_dsl_raises_error(self):
        with pytest.raises(DSLCompilerError, match="DSL input is empty"):
            compile_dsl_text("")
    
    def test_compile_no_blocks_raises_error(self):
        with pytest.raises(DSLCompilerError, match="No DSL blocks"):
            compile_dsl_text("Just plain text without any code blocks")
    
    def test_unknown_blocks_ignored(self):
        dsl = """```report
id: RPT-001
```

```unknown_block
content: value
```"""
        result = compile_dsl_text(dsl)
        assert result["report"]["id"] == "RPT-001"
        # Unknown block should be ignored


class TestDSLSeverityNormalization:
    """Test severity value normalization during compilation."""
    
    def test_severity_normalized_to_standard_values(self):
        dsl = """```finding
id: F-001
title: Test Finding
severity: critical
```

```finding
id: F-002
title: Another Finding
severity: HIGH
```"""
        result = compile_dsl_text(dsl)
        
        severities = [f["severity"] for f in result["findings"]]
        assert "Critical" in severities
        assert "High" in severities
    
    def test_finding_sorting_by_severity(self):
        dsl = """```finding
id: F-001
title: Low Finding
severity: low
```

```finding
id: F-002
title: Critical Finding
severity: critical
```

```finding
id: F-003
title: High Finding
severity: high
```"""
        result = compile_dsl_text(dsl)
        
        # Should be sorted by severity (Critical first, then High, then Low)
        assert result["findings"][0]["severity"] == "Critical"
        assert result["findings"][1]["severity"] == "High"
        assert result["findings"][2]["severity"] == "Low"
