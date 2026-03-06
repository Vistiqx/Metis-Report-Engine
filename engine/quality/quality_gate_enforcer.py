"""Quality gate enforcer for Metis Report Engine.

Enforces report quality gates with "Block with Warning" behavior:
- Blocks PDF generation by default on quality gate failures
- Allows override via skip_quality_gates parameter
- Returns detailed quality report with warnings and errors
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from enum import Enum


class GateSeverity(Enum):
    """Quality gate severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class QualityGateResult:
    """Result of quality gate enforcement."""
    
    def __init__(self):
        self.passed = True
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.info: List[Dict[str, Any]] = []
        self.summary = ""
    
    def add_error(self, gate: str, message: str, details: Optional[Dict] = None):
        """Add an error-level quality gate failure."""
        self.errors.append({
            "gate": gate,
            "severity": GateSeverity.ERROR.value,
            "message": message,
            "details": details or {},
        })
        self.passed = False
    
    def add_warning(self, gate: str, message: str, details: Optional[Dict] = None):
        """Add a warning-level quality gate issue."""
        self.warnings.append({
            "gate": gate,
            "severity": GateSeverity.WARNING.value,
            "message": message,
            "details": details or {},
        })
    
    def add_info(self, gate: str, message: str, details: Optional[Dict] = None):
        """Add an info-level quality gate notice."""
        self.info.append({
            "gate": gate,
            "severity": GateSeverity.INFO.value,
            "message": message,
            "details": details or {},
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "summary": self._generate_summary(),
        }
    
    def _generate_summary(self) -> str:
        """Generate human-readable summary."""
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        if not parts:
            return "All quality gates passed"
        return "; ".join(parts)


# Define all quality gates
REQUIRED_GATES = [
    "schema_validation",
    "required_sections",
    "reference_resolution",
    "severity_normalization",
    "visualization_validity",
    "executive_summary",
    "findings_count",
]


def enforce_quality_gates(
    report_json: Dict[str, Any],
    gates: Optional[List[str]] = None,
    strict: bool = False,
) -> QualityGateResult:
    """Enforce quality gates on a report.
    
    Args:
        report_json: The report to validate
        gates: List of gates to enforce (default: all)
        strict: If True, warnings also block
        
    Returns:
        QualityGateResult with detailed results
    """
    result = QualityGateResult()
    gates_to_check = gates or REQUIRED_GATES
    
    # Gate 1: Schema validation
    if "schema_validation" in gates_to_check:
        _check_schema_validation(report_json, result)
    
    # Gate 2: Required sections
    if "required_sections" in gates_to_check:
        _check_required_sections(report_json, result)
    
    # Gate 3: Reference resolution
    if "reference_resolution" in gates_to_check:
        _check_reference_resolution(report_json, result)
    
    # Gate 4: Severity normalization
    if "severity_normalization" in gates_to_check:
        _check_severity_normalization(report_json, result)
    
    # Gate 5: Visualization validity
    if "visualization_validity" in gates_to_check:
        _check_visualization_validity(report_json, result)
    
    # Gate 6: Executive summary
    if "executive_summary" in gates_to_check:
        _check_executive_summary(report_json, result)
    
    # Gate 7: Findings count
    if "findings_count" in gates_to_check:
        _check_findings_count(report_json, result)
    
    return result


def _check_schema_validation(report_json: Dict[str, Any], result: QualityGateResult):
    """Check that report passes schema validation."""
    from engine.parser.schema_validator import validate_report_with_details
    
    validation = validate_report_with_details(report_json)
    
    if not validation.get("valid", False):
        error_details = validation.get("error", {})
        result.add_error(
            "schema_validation",
            f"Schema validation failed: {error_details.get('message', 'Unknown error')}",
            {"validation_errors": error_details.get("details", [])},
        )
    else:
        result.add_info("schema_validation", "Schema validation passed")


def _check_required_sections(report_json: Dict[str, Any], result: QualityGateResult):
    """Check that all required sections exist."""
    required_sections = ["report", "findings", "evidence", "recommendations"]
    
    missing = []
    for section in required_sections:
        if section not in report_json:
            missing.append(section)
    
    if missing:
        result.add_error(
            "required_sections",
            f"Missing required sections: {', '.join(missing)}",
            {"missing_sections": missing},
        )
    else:
        result.add_info("required_sections", "All required sections present")


def _check_reference_resolution(report_json: Dict[str, Any], result: QualityGateResult):
    """Check that evidence and recommendation references resolve."""
    evidence_map = {e.get("id"): e for e in report_json.get("evidence", []) if e.get("id")}
    recommendation_map = {r.get("id"): r for r in report_json.get("recommendations", []) if r.get("id")}
    
    unresolved_evidence = []
    unresolved_recommendations = []
    
    for finding in report_json.get("findings", []):
        # Check evidence refs
        for ref in finding.get("evidence_refs", []):
            if ref not in evidence_map:
                unresolved_evidence.append({"finding": finding.get("id"), "ref": ref})
        
        # Check recommendation refs
        for ref in finding.get("recommendation_refs", []):
            if ref not in recommendation_map:
                unresolved_recommendations.append({"finding": finding.get("id"), "ref": ref})
    
    if unresolved_evidence or unresolved_recommendations:
        details = {}
        if unresolved_evidence:
            details["unresolved_evidence"] = unresolved_evidence
        if unresolved_recommendations:
            details["unresolved_recommendations"] = unresolved_recommendations
        
        result.add_error(
            "reference_resolution",
            f"Found {len(unresolved_evidence)} unresolved evidence and {len(unresolved_recommendations)} unresolved recommendation references",
            details,
        )
    else:
        result.add_info("reference_resolution", "All references resolve correctly")


def _check_severity_normalization(report_json: Dict[str, Any], result: QualityGateResult):
    """Check that severity values are normalized."""
    valid_severities = {"Critical", "High", "Medium", "Low", "Informational"}
    invalid_findings = []
    
    for finding in report_json.get("findings", []):
        severity = finding.get("severity", "")
        if severity and severity not in valid_severities:
            invalid_findings.append({
                "id": finding.get("id"),
                "severity": severity,
            })
    
    if invalid_findings:
        result.add_error(
            "severity_normalization",
            f"Found {len(invalid_findings)} finding(s) with non-normalized severity values",
            {"invalid_findings": invalid_findings},
        )
    else:
        result.add_info("severity_normalization", "All severity values normalized")


def _check_visualization_validity(report_json: Dict[str, Any], result: QualityGateResult):
    """Check that visualizations have valid data sources."""
    visualizations = report_json.get("visualizations", [])
    invalid_viz = []
    
    for viz in visualizations:
        data_source = viz.get("data_source", "")
        if data_source:
            # Simple check: data source should be dot-notation path
            parts = data_source.split(".")
            data = report_json
            for part in parts:
                if isinstance(data, dict) and part in data:
                    data = data[part]
                else:
                    invalid_viz.append({
                        "id": viz.get("id"),
                        "data_source": data_source,
                        "reason": "Path not found in report",
                    })
                    break
    
    if invalid_viz:
        result.add_warning(
            "visualization_validity",
            f"Found {len(invalid_viz)} visualization(s) with invalid data sources",
            {"invalid_visualizations": invalid_viz},
        )
    else:
        result.add_info("visualization_validity", "All visualizations have valid data sources")


def _check_executive_summary(report_json: Dict[str, Any], result: QualityGateResult):
    """Check that executive summary exists (warning only)."""
    executive = report_json.get("executive_summary", {})
    
    if not executive:
        result.add_warning(
            "executive_summary",
            "No executive summary present",
            {},
        )
    elif not executive.get("summary"):
        result.add_warning(
            "executive_summary",
            "Executive summary present but empty",
            {},
        )
    else:
        result.add_info("executive_summary", "Executive summary present")


def _check_findings_count(report_json: Dict[str, Any], result: QualityGateResult):
    """Check that at least one finding exists."""
    findings = report_json.get("findings", [])
    
    if len(findings) == 0:
        result.add_error(
            "findings_count",
            "Report has no findings",
            {"findings_count": 0},
        )
    elif len(findings) < 2:
        result.add_warning(
            "findings_count",
            f"Report has only {len(findings)} finding(s)",
            {"findings_count": len(findings)},
        )
    else:
        result.add_info("findings_count", f"Report has {len(findings)} findings")


def should_block_generation(
    result: QualityGateResult,
    skip_gates: bool = False,
    strict: bool = False,
) -> bool:
    """Determine if report generation should be blocked.
    
    Args:
        result: Quality gate result
        skip_gates: Whether to skip quality gate enforcement
        strict: If True, warnings also block
        
    Returns:
        True if generation should be blocked
    """
    if skip_gates:
        return False
    
    if result.errors:
        return True
    
    if strict and result.warnings:
        return True
    
    return False
