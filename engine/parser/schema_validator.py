"""Schema validation with structured error model for Metis Report Engine.

This module provides validation against JSON schemas with structured,
actionable error messages following the error model specification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schema"
MASTER_SCHEMA = SCHEMA_ROOT / "metis_report.schema.json"
DSL_SCHEMA = SCHEMA_ROOT / "metis_report_dsl.schema.json"


class StructuredValidationError(Exception):
    """Raised when validation fails with structured error information."""
    
    def __init__(self, error_envelope: Dict[str, Any]):
        self.error_envelope = error_envelope
        super().__init__(error_envelope.get("error", {}).get("message", "Validation failed"))


def validate_report_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate canonical report JSON against the master schema.
    
    Args:
        payload: The report JSON to validate
        
    Returns:
        Validation result with status
        
    Raises:
        StructuredValidationError: If validation fails with detailed error info
    """
    # Load all schema files into a registry
    schema_registry, base_schemas = _load_schema_registry()
    
    # Load the master schema and inline all $refs
    with MASTER_SCHEMA.open("r", encoding="utf-8") as handle:
        raw_schema = json.load(handle)
    
    schema = _resolve_refs(raw_schema, schema_registry, base_schemas, "", set())
    
    # Validate
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))
    
    if errors:
        error_envelope = build_error_envelope(
            code="SCHEMA_VALIDATION_FAILED",
            stage="validation",
            message=f"Report validation failed with {len(errors)} error(s)",
            validation_errors=errors,
        )
        raise StructuredValidationError(error_envelope)
    
    return {"valid": True, "status": "passed"}


def _load_schema_registry() -> tuple[Dict[str, Any], Dict[str, str]]:
    """Load all schema files into a registry.
    
    Returns:
        Tuple of (registry dict, base_schemas dict mapping schema names to their base paths)
    """
    registry = {}
    base_schemas = {}  # Track which base directory each schema is from
    
    for schema_file in SCHEMA_ROOT.rglob("*.json"):
        try:
            with schema_file.open("r", encoding="utf-8") as f:
                schema = json.load(f)
                
            # Store with relative path from schema root
            rel_path = schema_file.relative_to(SCHEMA_ROOT).as_posix()
            registry[rel_path] = schema
            base_schemas[rel_path] = schema_file.parent.relative_to(SCHEMA_ROOT).as_posix()
            
            # Also store with $id if present
            if "$id" in schema:
                registry[schema["$id"]] = schema
                base_schemas[schema["$id"]] = schema_file.parent.relative_to(SCHEMA_ROOT).as_posix()
                
        except (json.JSONDecodeError, IOError):
            continue
    
    return registry, base_schemas


def _resolve_refs(
    schema: Any, 
    registry: Dict[str, Any], 
    base_schemas: Dict[str, str],
    current_base: str,
    resolved_refs: set
) -> Any:
    """Recursively resolve $ref references in a schema.
    
    Args:
        schema: The schema or subschema to process
        registry: Registry of loaded schemas
        base_schemas: Mapping of schema names to their base directories
        current_base: Current base directory for relative refs
        resolved_refs: Set of already-resolved refs to avoid infinite recursion
        
    Returns:
        Schema with refs resolved
    """
    if not isinstance(schema, dict):
        return schema
    
    # Handle $ref
    if "$ref" in schema:
        ref_path = schema["$ref"]
        
        # Skip if already resolved to avoid infinite recursion
        ref_key = f"{current_base}/{ref_path}" if current_base else ref_path
        if ref_key in resolved_refs:
            return {"type": "object"}  # Fallback
        
        # Calculate the lookup key based on current base
        if ref_path.startswith("./"):
            # Relative reference - resolve against current base
            if current_base:
                # Remove ./ and prepend current base
                ref_name = ref_path[2:]  # Remove ./
                lookup_key = f"{current_base}/{ref_name}" if current_base else ref_name
            else:
                lookup_key = ref_path[2:]
        elif ref_path.startswith("../"):
            # Parent directory reference - navigate up from current base
            if current_base:
                # Go up one directory level from current_base
                parent_base = str(Path(current_base).parent)
                ref_name = ref_path[3:]  # Remove ../
                if parent_base and parent_base != ".":
                    lookup_key = f"{parent_base}/{ref_name}"
                else:
                    lookup_key = ref_name
            else:
                lookup_key = ref_path[3:]
        else:
            lookup_key = ref_path
        
        # Look up the reference
        if lookup_key in registry:
            new_resolved = resolved_refs | {ref_key}
            # Get the base directory for this schema
            new_base = base_schemas.get(lookup_key, current_base)
            resolved_schema = _resolve_refs(registry[lookup_key], registry, base_schemas, new_base, new_resolved)
            
            # Merge with any sibling properties (like additionalProperties)
            result = dict(resolved_schema)
            for key, value in schema.items():
                if key != "$ref":
                    result[key] = _resolve_refs(value, registry, base_schemas, current_base, resolved_refs)
            return result
        
        # If ref not found, try without the base prefix
        if lookup_key != ref_path and ref_path in registry:
            new_resolved = resolved_refs | {ref_key}
            new_base = base_schemas.get(ref_path, current_base)
            resolved_schema = _resolve_refs(registry[ref_path], registry, base_schemas, new_base, new_resolved)
            
            result = dict(resolved_schema)
            for key, value in schema.items():
                if key != "$ref":
                    result[key] = _resolve_refs(value, registry, base_schemas, current_base, resolved_refs)
            return result
        
        # If still not found, return as-is
        return schema
    
    # Recursively process all properties
    result = {}
    for key, value in schema.items():
        if isinstance(value, dict):
            result[key] = _resolve_refs(value, registry, base_schemas, current_base, resolved_refs)
        elif isinstance(value, list):
            result[key] = [
                _resolve_refs(item, registry, base_schemas, current_base, resolved_refs) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result


def validate_dsl_payload(dsl_text: str) -> Dict[str, Any]:
    """Validate DSL text structure (basic structural validation).
    
    Args:
        dsl_text: The DSL text to validate
        
    Returns:
        Validation result with status
        
    Raises:
        StructuredValidationError: If validation fails
    """
    if not dsl_text or not dsl_text.strip():
        error_envelope = build_error_envelope(
            code="DSL_PARSE_FAILED",
            stage="parsing",
            message="DSL input is empty",
        )
        raise StructuredValidationError(error_envelope)
    
    # Check for required report block
    if "```report" not in dsl_text:
        error_envelope = build_error_envelope(
            code="MISSING_REQUIRED_SECTION",
            stage="parsing",
            message="DSL is missing required 'report' block",
        )
        raise StructuredValidationError(error_envelope)
    
    # Basic block structure validation
    open_count = dsl_text.count("```")
    if open_count % 2 != 0:
        error_envelope = build_error_envelope(
            code="DSL_PARSE_FAILED",
            stage="parsing",
            message="DSL has mismatched code block delimiters",
        )
        raise StructuredValidationError(error_envelope)
    
    return {"valid": True, "status": "passed"}


def build_error_envelope(
    code: str,
    stage: str,
    message: str,
    validation_errors: Optional[List[ValidationError]] = None,
    retryable: bool = False,
) -> Dict[str, Any]:
    """Build a structured error envelope per the error model specification.
    
    Args:
        code: Error code (e.g., SCHEMA_VALIDATION_FAILED)
        stage: Pipeline stage where error occurred
        message: Human-readable error message
        validation_errors: List of jsonschema ValidationError objects
        retryable: Whether the operation can be retried
        
    Returns:
        Structured error envelope dictionary
    """
    details = []
    if validation_errors:
        for error in validation_errors:
            detail = {
                "path": list(error.path),
                "message": error.message,
                "schema_path": list(error.schema_path),
            }
            # Add context for common error types
            if error.context:
                detail["context"] = [str(ctx.message) for ctx in error.context]
            details.append(detail)
    
    return {
        "error": {
            "code": code,
            "message": message,
            "stage": stage,
            "details": details,
            "retryable": retryable,
        }
    }


def format_validation_errors(errors: List[ValidationError]) -> List[str]:
    """Format validation errors into human-readable strings.
    
    Args:
        errors: List of ValidationError objects
        
    Returns:
        List of formatted error messages
    """
    formatted = []
    for error in sorted(errors, key=lambda e: e.path):
        path = ".".join(str(p) for p in error.path) if error.path else "root"
        formatted.append(f"[{path}] {error.message}")
    return formatted


def validate_report_with_details(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate report and return detailed results without raising.
    
    This is useful for API endpoints that need to return validation
    results without throwing exceptions.
    
    Args:
        payload: The report JSON to validate
        
    Returns:
        Dictionary with valid status and any errors
    """
    try:
        return validate_report_payload(payload)
    except StructuredValidationError as e:
        return {
            "valid": False,
            "status": "failed",
            "error": e.error_envelope["error"],
        }


def validate_dsl_with_details(dsl_text: str) -> Dict[str, Any]:
    """Validate DSL and return detailed results without raising.
    
    Args:
        dsl_text: The DSL text to validate
        
    Returns:
        Dictionary with valid status and any errors
    """
    try:
        return validate_dsl_payload(dsl_text)
    except StructuredValidationError as e:
        return {
            "valid": False,
            "status": "failed",
            "error": e.error_envelope["error"],
        }
