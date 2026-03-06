
"""Report linter for Metis Report Engine.

The linter performs quality-oriented checks beyond schema validation.
It is intended to catch weak, incomplete, or low-confidence reports
before final rendering or client delivery.
"""

from __future__ import annotations

from typing import Any, Dict, List


def lint_report(report_json: Dict[str, Any]) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []

    if not report_json.get("executive_summary"):
        issues.append(_issue("warning", "missing_executive_summary", "Executive summary is missing."))

    findings = report_json.get("findings", [])
    if not findings:
        issues.append(_issue("error", "missing_findings", "Report contains no findings."))

    if not report_json.get("visualizations"):
        issues.append(_issue("warning", "missing_visualizations", "No visualizations are defined."))

    for finding in findings:
        fid = finding.get("id", "UNKNOWN")
        if not finding.get("severity"):
            issues.append(_issue("error", "missing_severity", f"Finding {fid} is missing severity."))
        if not finding.get("recommendation_refs"):
            issues.append(_issue("warning", "missing_recommendations", f"Finding {fid} has no recommendation references."))
        if not finding.get("evidence_refs"):
            issues.append(_issue("warning", "missing_evidence", f"Finding {fid} has no evidence references."))

    return issues


def _issue(level: str, code: str, message: str) -> Dict[str, str]:
    return {"level": level, "code": code, "message": message}
