"""Report diff engine for comparing two canonical reports."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set


def diff_reports(
    old_report: Dict[str, Any],
    new_report: Dict[str, Any],
    include_content_diff: bool = True,
) -> Dict[str, Any]:
    """Compare two reports and return detailed diff.

    Args:
        old_report: The baseline report
        new_report: The new report to compare against baseline
        include_content_diff: Whether to include detailed content changes

    Returns:
        Dictionary containing:
        - added_findings: List of new finding IDs
        - removed_findings: List of removed finding IDs
        - severity_changes: List of severity changes with details
        - content_changes: List of content changes (if include_content_diff=True)
        - recommendation_changes: Changes to recommendations
        - evidence_changes: Changes to evidence
        - metrics_changes: Changes to metrics
        - summary: Human-readable summary
        - change_classification: Breaking/Significant/Cosmetic
    """
    result = {
        "added_findings": [],
        "removed_findings": [],
        "severity_changes": [],
        "content_changes": [],
        "recommendation_changes": [],
        "evidence_changes": [],
        "metrics_changes": {},
        "summary": "",
        "change_classification": "none",
        "total_changes": 0,
    }

    # Compare findings
    old_findings = {item.get("id"): item for item in old_report.get("findings", []) if item.get("id")}
    new_findings = {item.get("id"): item for item in new_report.get("findings", []) if item.get("id")}

    # Added findings
    added_ids = set(new_findings.keys()) - set(old_findings.keys())
    result["added_findings"] = sorted(list(added_ids))

    # Removed findings
    removed_ids = set(old_findings.keys()) - set(new_findings.keys())
    result["removed_findings"] = sorted(list(removed_ids))

    # Severity changes and content changes
    common_ids = set(old_findings.keys()) & set(new_findings.keys())
    for fid in common_ids:
        old_f = old_findings[fid]
        new_f = new_findings[fid]

        # Check severity change
        old_sev = old_f.get("severity")
        new_sev = new_f.get("severity")
        if old_sev != new_sev:
            result["severity_changes"].append({
                "id": fid,
                "old_severity": old_sev,
                "new_severity": new_sev,
            })

        # Check content changes if requested
        if include_content_diff:
            content_changes = _compare_finding_content(old_f, new_f)
            if content_changes:
                result["content_changes"].append({
                    "id": fid,
                    "changes": content_changes,
                })

    # Compare recommendations
    result["recommendation_changes"] = _compare_recommendations(
        old_report.get("recommendations", []),
        new_report.get("recommendations", []),
    )

    # Compare evidence
    result["evidence_changes"] = _compare_evidence(
        old_report.get("evidence", []),
        new_report.get("evidence", []),
    )

    # Compare metrics
    result["metrics_changes"] = _compare_metrics(
        old_report.get("metrics", {}),
        new_report.get("metrics", {}),
    )

    # Calculate total changes
    result["total_changes"] = (
        len(result["added_findings"]) +
        len(result["removed_findings"]) +
        len(result["severity_changes"]) +
        len(result["content_changes"]) +
        len(result["recommendation_changes"]) +
        len(result["evidence_changes"])
    )

    # Generate summary and classification
    result["summary"] = _generate_summary(result)
    result["change_classification"] = _classify_changes(result)

    return result


def _compare_finding_content(old_f: Dict[str, Any], new_f: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compare content fields of two findings."""
    changes = []
    content_fields = ["title", "summary", "description", "category", "domain"]

    for field in content_fields:
        old_val = old_f.get(field)
        new_val = new_f.get(field)
        if old_val != new_val:
            changes.append({
                "field": field,
                "old_value": old_val,
                "new_value": new_val,
            })

    return changes


def _compare_recommendations(old_recs: List[Dict], new_recs: List[Dict]) -> List[Dict[str, Any]]:
    """Compare recommendations between two reports."""
    changes = []

    old_map = {r.get("id"): r for r in old_recs if r.get("id")}
    new_map = {r.get("id"): r for r in new_recs if r.get("id")}

    # Added recommendations
    added = set(new_map.keys()) - set(old_map.keys())
    for rid in added:
        changes.append({
            "type": "added",
            "id": rid,
            "details": new_map[rid],
        })

    # Removed recommendations
    removed = set(old_map.keys()) - set(new_map.keys())
    for rid in removed:
        changes.append({
            "type": "removed",
            "id": rid,
            "details": old_map[rid],
        })

    # Changed recommendations
    common = set(old_map.keys()) & set(new_map.keys())
    for rid in common:
        old_rec = old_map[rid]
        new_rec = new_map[rid]

        rec_changes = {}
        for field in ["title", "priority", "summary", "action"]:
            if old_rec.get(field) != new_rec.get(field):
                rec_changes[field] = {
                    "old": old_rec.get(field),
                    "new": new_rec.get(field),
                }

        if rec_changes:
            changes.append({
                "type": "modified",
                "id": rid,
                "changes": rec_changes,
            })

    return changes


def _compare_evidence(old_ev: List[Dict], new_ev: List[Dict]) -> List[Dict[str, Any]]:
    """Compare evidence between two reports."""
    changes = []

    old_map = {e.get("id"): e for e in old_ev if e.get("id")}
    new_map = {e.get("id"): e for e in new_ev if e.get("id")}

    # Added evidence
    added = set(new_map.keys()) - set(old_map.keys())
    for eid in added:
        changes.append({
            "type": "added",
            "id": eid,
            "details": new_map[eid],
        })

    # Removed evidence
    removed = set(old_map.keys()) - set(new_map.keys())
    for eid in removed:
        changes.append({
            "type": "removed",
            "id": eid,
            "details": old_map[eid],
        })

    return changes


def _compare_metrics(old_metrics: Dict, new_metrics: Dict) -> Dict[str, Any]:
    """Compare metrics between two reports."""
    changes = {}

    # Compare risk distribution
    old_dist = old_metrics.get("risk_distribution", {})
    new_dist = new_metrics.get("risk_distribution", {})

    for severity in ["critical", "high", "medium", "low"]:
        old_count = old_dist.get(severity, 0)
        new_count = new_dist.get(severity, 0)
        if old_count != new_count:
            changes[f"risk_{severity}"] = {
                "old": old_count,
                "new": new_count,
                "delta": new_count - old_count,
            }

    return changes


def _generate_summary(diff_result: Dict[str, Any]) -> str:
    """Generate human-readable summary of changes."""
    parts = []

    if diff_result["added_findings"]:
        count = len(diff_result["added_findings"])
        parts.append(f"{count} new finding{'s' if count > 1 else ''} added")

    if diff_result["removed_findings"]:
        count = len(diff_result["removed_findings"])
        parts.append(f"{count} finding{'s' if count > 1 else ''} removed")

    if diff_result["severity_changes"]:
        count = len(diff_result["severity_changes"])
        parts.append(f"{count} severity change{'s' if count > 1 else ''}")

    if diff_result["content_changes"]:
        count = len(diff_result["content_changes"])
        parts.append(f"{count} finding{'s' if count > 1 else ''} with content updates")

    if diff_result["recommendation_changes"]:
        count = len(diff_result["recommendation_changes"])
        parts.append(f"{count} recommendation change{'s' if count > 1 else ''}")

    if diff_result["evidence_changes"]:
        count = len(diff_result["evidence_changes"])
        parts.append(f"{count} evidence change{'s' if count > 1 else ''}")

    if not parts:
        return "No changes detected"

    return "; ".join(parts)


def _classify_changes(diff_result: Dict[str, Any]) -> str:
    """Classify overall change severity."""
    # First check: Severity increases (e.g., Low -> Critical) are breaking
    for change in diff_result.get("severity_changes", []):
        severity_order = ["Informational", "Low", "Medium", "High", "Critical"]
        old_sev = change.get("old_severity", "")
        new_sev = change.get("new_severity", "")
        
        if old_sev in severity_order and new_sev in severity_order:
            old_idx = severity_order.index(old_sev)
            new_idx = severity_order.index(new_sev)
            if new_idx > old_idx:  # Higher index = higher severity (breaking)
                return "breaking"

    # Second check: Added or removed findings are significant
    if diff_result.get("added_findings") or diff_result.get("removed_findings"):
        return "significant"

    # Third check: Any content changes without severity changes are cosmetic
    if diff_result.get("total_changes", 0) > 0:
        return "cosmetic"

    return "none"


def generate_diff_report(diff_result: Dict[str, Any], format: str = "markdown") -> str:
    """Generate a formatted diff report.

    Args:
        diff_result: The diff result from diff_reports()
        format: Output format (markdown or html)

    Returns:
        Formatted diff report
    """
    if format == "markdown":
        return _generate_markdown_diff(diff_result)
    elif format == "html":
        return _generate_html_diff(diff_result)
    else:
        raise ValueError(f"Unsupported format: {format}")


def _generate_markdown_diff(diff_result: Dict[str, Any]) -> str:
    """Generate Markdown formatted diff report."""
    lines = ["# Report Comparison", ""]

    lines.append(f"**Change Classification:** {diff_result['change_classification'].upper()}")
    lines.append(f"**Total Changes:** {diff_result['total_changes']}")
    lines.append("")
    lines.append(f"**Summary:** {diff_result['summary']}")
    lines.append("")

    # Added findings
    if diff_result["added_findings"]:
        lines.append("## New Findings")
        lines.append("")
        for fid in diff_result["added_findings"]:
            lines.append(f"- **{fid}** — Added")
        lines.append("")

    # Removed findings
    if diff_result["removed_findings"]:
        lines.append("## Removed Findings")
        lines.append("")
        for fid in diff_result["removed_findings"]:
            lines.append(f"- **{fid}** — Removed")
        lines.append("")

    # Severity changes
    if diff_result["severity_changes"]:
        lines.append("## Severity Changes")
        lines.append("")
        for change in diff_result["severity_changes"]:
            lines.append(f"- **{change['id']}:** {change['old_severity']} → {change['new_severity']}")
        lines.append("")

    # Content changes
    if diff_result["content_changes"]:
        lines.append("## Content Updates")
        lines.append("")
        for change in diff_result["content_changes"]:
            lines.append(f"### {change['id']}")
            lines.append("")
            for field_change in change["changes"]:
                lines.append(f"- **{field_change['field']}:** Updated")
            lines.append("")

    return "\n".join(lines)


def _generate_html_diff(diff_result: Dict[str, Any]) -> str:
    """Generate HTML formatted diff report."""
    html = ["<html><body>"]
    html.append("<h1>Report Comparison</h1>")

    cls = diff_result['change_classification']
    color = {"breaking": "red", "significant": "orange", "cosmetic": "blue", "none": "green"}.get(cls, "black")
    html.append(f'<p><strong>Change Classification:</strong> <span style="color: {color};">{cls.upper()}</span></p>')
    html.append(f"<p><strong>Total Changes:</strong> {diff_result['total_changes']}</p>")
    html.append(f"<p><strong>Summary:</strong> {diff_result['summary']}</p>")

    if diff_result["added_findings"]:
        html.append("<h2>New Findings</h2><ul>")
        for fid in diff_result["added_findings"]:
            html.append(f"<li><strong>{fid}</strong> — Added</li>")
        html.append("</ul>")

    if diff_result["removed_findings"]:
        html.append("<h2>Removed Findings</h2><ul>")
        for fid in diff_result["removed_findings"]:
            html.append(f"<li><strong>{fid}</strong> — Removed</li>")
        html.append("</ul>")

    html.append("</body></html>")
    return "".join(html)