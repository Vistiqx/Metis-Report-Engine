"""Tests for schema validator module."""

import pytest
from jsonschema import ValidationError
from engine.parser.schema_validator import (
    validate_dsl_payload,
    build_error_envelope,
    format_validation_errors,
    validate_dsl_with_details,
    StructuredValidationError,
    _load_schema_registry,
    _resolve_refs,
)


class TestValidateDSLPayload:
    """Test DSL text validation."""
    
    def test_valid_dsl_passes(self):
        dsl = """```report
id: RPT-001
title: Test Report
```

```finding
id: F-001
title: Test Finding
```"""
        
        result = validate_dsl_payload(dsl)
        assert result["valid"] is True
    
    def test_empty_dsl_fails(self):
        with pytest.raises(StructuredValidationError) as exc_info:
            validate_dsl_payload("")
        
        error = exc_info.value.error_envelope["error"]
        assert error["code"] == "DSL_PARSE_FAILED"
        assert error["stage"] == "parsing"
        assert "empty" in error["message"].lower()
    
    def test_whitespace_only_dsl_fails(self):
        with pytest.raises(StructuredValidationError) as exc_info:
            validate_dsl_payload("   \n\t  ")
        
        error = exc_info.value.error_envelope["error"]
        assert error["code"] == "DSL_PARSE_FAILED"
    
    def test_missing_report_block_fails(self):
        dsl = """```finding
id: F-001
title: Test Finding
```"""
        
        with pytest.raises(StructuredValidationError) as exc_info:
            validate_dsl_payload(dsl)
        
        error = exc_info.value.error_envelope["error"]
        assert error["code"] == "MISSING_REQUIRED_SECTION"
        assert "report" in error["message"].lower()
    
    def test_mismatched_delimiters_fails(self):
        dsl = """```report
id: RPT-001
```

```finding
id: F-001
"""  # Missing closing ```
        
        with pytest.raises(StructuredValidationError) as exc_info:
            validate_dsl_payload(dsl)
        
        error = exc_info.value.error_envelope["error"]
        assert error["code"] == "DSL_PARSE_FAILED"
        assert "mismatched" in error["message"].lower() or "delimiter" in error["message"].lower()


class TestBuildErrorEnvelope:
    """Test error envelope construction."""
    
    def test_basic_error_envelope(self):
        envelope = build_error_envelope(
            code="TEST_ERROR",
            stage="test_stage",
            message="Test error message",
        )
        
        assert envelope["error"]["code"] == "TEST_ERROR"
        assert envelope["error"]["stage"] == "test_stage"
        assert envelope["error"]["message"] == "Test error message"
        assert envelope["error"]["retryable"] is False
        assert envelope["error"]["details"] == []
    
    def test_error_envelope_with_retryable(self):
        envelope = build_error_envelope(
            code="RETRYABLE_ERROR",
            stage="test",
            message="Can retry",
            retryable=True,
        )
        
        assert envelope["error"]["retryable"] is True
    
    def test_error_envelope_with_validation_errors(self):
        # Create mock validation errors using the correct constructor
        mock_error1 = ValidationError(
            message="'title' is a required property",
            validator="required",
            path=("findings", 0),
            schema_path=("properties", "findings", "items", "required"),
        )
        mock_error2 = ValidationError(
            message="'id' is a required property",
            validator="required",
            path=("evidence", 0),
            schema_path=("properties", "evidence", "items", "required"),
        )
        
        envelope = build_error_envelope(
            code="SCHEMA_VALIDATION_FAILED",
            stage="validation",
            message="Validation failed",
            validation_errors=[mock_error1, mock_error2],
        )
        
        details = envelope["error"]["details"]
        assert len(details) == 2
        assert details[0]["path"] == ["findings", 0]
        assert "title" in details[0]["message"]
        assert details[1]["path"] == ["evidence", 0]


class TestFormatValidationErrors:
    """Test validation error formatting."""
    
    def test_format_single_error(self):
        mock_error = ValidationError(
            message="'title' is a required property",
            validator="required",
            path=("findings", 0),
            schema_path=(),
        )
        
        formatted = format_validation_errors([mock_error])
        
        assert len(formatted) == 1
        assert "findings.0" in formatted[0]
        assert "title" in formatted[0]
    
    def test_format_multiple_errors(self):
        mock_errors = [
            ValidationError(
                message="Error 1",
                validator="required",
                path=("a", "b"),
                schema_path=(),
            ),
            ValidationError(
                message="Error 2",
                validator="type",
                path=("c",),
                schema_path=(),
            ),
        ]
        
        formatted = format_validation_errors(mock_errors)
        
        assert len(formatted) == 2
        assert "a.b" in formatted[0]
        assert "c" in formatted[1]
    
    def test_format_error_with_empty_path(self):
        mock_error = ValidationError(
            message="Root error",
            validator="required",
            path=(),
            schema_path=(),
        )
        
        formatted = format_validation_errors([mock_error])
        
        assert "root" in formatted[0]


class TestValidateDSLWithDetails:
    """Test non-throwing DSL validation."""
    
    def test_returns_success_for_valid_dsl(self):
        dsl = """```report
id: RPT-001
title: Test
```"""
        
        result = validate_dsl_with_details(dsl)
        
        assert result["valid"] is True
        assert result["status"] == "passed"
    
    def test_returns_failure_for_invalid_dsl(self):
        result = validate_dsl_with_details("")
        
        assert result["valid"] is False
        assert result["status"] == "failed"
        assert "error" in result
        assert result["error"]["code"] == "DSL_PARSE_FAILED"


class TestStructuredValidationError:
    """Test the structured validation error exception."""
    
    def test_exception_contains_error_envelope(self):
        envelope = {
            "error": {
                "code": "TEST_ERROR",
                "message": "Test message",
                "stage": "test",
                "details": [],
                "retryable": False,
            }
        }
        
        exc = StructuredValidationError(envelope)
        
        assert exc.error_envelope == envelope
        assert str(exc) == "Test message"
    
    def test_exception_uses_default_message(self):
        envelope = {"error": {}}  # Missing message
        
        exc = StructuredValidationError(envelope)
        
        assert "Validation failed" in str(exc)


class TestSchemaRegistry:
    """Test schema loading and resolution."""
    
    def test_load_schema_registry(self):
        registry, base_schemas = _load_schema_registry()
        
        # Should load main schemas
        assert "metis_report.schema.json" in registry
        assert "core/finding.schema.json" in registry
        assert "core/evidence.schema.json" in registry
        assert "core/recommendation.schema.json" in registry
    
    def test_resolve_refs_inlines_simple_refs(self):
        registry, base_schemas = _load_schema_registry()
        
        # Get a simple schema with refs
        test_schema = {
            "type": "object",
            "properties": {
                "finding": {"$ref": "./core/finding.schema.json"}
            }
        }
        
        # Resolve refs with current base = ""
        resolved = _resolve_refs(test_schema, registry, base_schemas, "", set())
        
        # The finding property should now have the inlined schema
        assert "finding" in resolved["properties"]
        # Should have inlined the finding schema which has 'properties' and 'required'
        finding_schema = resolved["properties"]["finding"]
        assert "properties" in finding_schema or "type" in finding_schema
    
    def test_resolve_refs_handles_circular_refs(self):
        registry, base_schemas = _load_schema_registry()
        
        # Test with a schema that might have circular refs
        master = registry.get("metis_report.schema.json", {})
        if master:
            resolved = _resolve_refs(master, registry, base_schemas, "", set())
            # Should not raise recursion error
            assert "properties" in resolved or "type" in resolved
