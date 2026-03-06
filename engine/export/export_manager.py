
"""Export manager for Metis Report Engine."""

from __future__ import annotations

import json
from typing import Any, Dict


def export_report(report_json: Dict[str, Any], export_format: str) -> str:
    fmt = export_format.lower()

    if fmt == "json":
        return json.dumps(report_json, indent=2)

    if fmt == "markdown":
        return export_markdown(report_json)

    if fmt == "html":
        return export_html_placeholder(report_json)

    if fmt == "pdf":
        raise NotImplementedError("PDF export should be handled by the renderer.")

    raise ValueError(f"Unsupported export format: {export_format}")


def export_markdown(report_json: Dict[str, Any]) -> str:
    report = report_json.get("report", {})
    lines = [f"# {report.get('title', 'Untitled Report')}", ""]
    executive = report_json.get("executive_summary", {})
    if executive:
        lines.extend(["## Executive Summary", "", executive.get("summary", "No summary provided."), ""])
    findings = report_json.get("findings", [])
    if findings:
        lines.extend(["## Findings", ""])
        for finding in findings:
            lines.append(f"### {finding.get('id', 'F-000')} — {finding.get('title', 'Untitled Finding')}")
            lines.append(f"- Severity: {finding.get('severity', 'Informational')}")
            lines.append(f"- Summary: {finding.get('summary', '')}")
            lines.append("")
    return "\n".join(lines)


def export_html_placeholder(report_json: Dict[str, Any]) -> str:
    title = report_json.get("report", {}).get("title", "Untitled Report")
    return f"<html><body><h1>{title}</h1><p>HTML export placeholder.</p></body></html>"
