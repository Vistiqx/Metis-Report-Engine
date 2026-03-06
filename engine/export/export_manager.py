"""Export manager for Metis Report Engine.

Provides export functionality for multiple formats:
- JSON: Canonical report JSON
- Markdown: Human-readable text format
- HTML: Rich formatted document
- CSV: Tabular data for findings/recommendations
- PDF: Delegates to renderer pipeline
"""

from __future__ import annotations

import csv
import io
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from engine.renderer.html_renderer import render_report_html, render_professional_html
from engine.renderer.pdf_renderer import render_pdf_from_html


class ExportError(Exception):
    """Raised when export fails."""
    pass


def export_report(
    report_json: Dict[str, Any],
    export_format: str,
    *,
    template: Optional[str] = None,
    theme: Optional[str] = None,
    inline_css: bool = True,
) -> str:
    """Export report to specified format.

    Args:
        report_json: The canonical report JSON
        export_format: One of: json, markdown, html, csv, pdf
        template: Optional template name (for html/pdf)
        theme: Optional theme profile (for html/pdf)
        inline_css: Whether to inline CSS for standalone HTML

    Returns:
        Export result as string (or path for PDF)

    Raises:
        ExportError: If export fails
        ValueError: If format is unsupported
    """
    fmt = export_format.lower()

    if fmt == "json":
        return export_json(report_json)

    if fmt == "markdown":
        return export_markdown(report_json)

    if fmt == "html":
        return export_html(report_json, template=template, theme=theme, inline_css=inline_css)

    if fmt == "csv":
        return export_csv(report_json)

    if fmt == "pdf":
        # PDF returns file path, not content
        return export_pdf(report_json, template=template, theme=theme)

    raise ValueError(f"Unsupported export format: {export_format}")


def export_json(report_json: Dict[str, Any], indent: int = 2) -> str:
    """Export report to JSON format.

    Args:
        report_json: The report JSON
        indent: Indentation level for pretty printing

    Returns:
        JSON string
    """
    try:
        return json.dumps(report_json, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise ExportError(f"JSON serialization failed: {e}")


def export_markdown(report_json: Dict[str, Any]) -> str:
    """Export report to Markdown format.

    Args:
        report_json: The report JSON

    Returns:
        Markdown string
    """
    report = report_json.get("report", {})
    lines = []

    # Title and metadata
    lines.append(f"# {report.get('title', 'Untitled Report')}")
    lines.append("")

    if report.get("client"):
        lines.append(f"**Client:** {report['client']}")
    if report.get("classification"):
        lines.append(f"**Classification:** {report['classification']}")
    if report.get("version"):
        lines.append(f"**Version:** {report['version']}")
    if report.get("date_created"):
        lines.append(f"**Date:** {report['date_created']}")

    lines.append("")

    # Executive Summary
    executive = report_json.get("executive_summary", {})
    if executive:
        lines.append("## Executive Summary")
        lines.append("")
        if executive.get("overall_risk_rating"):
            lines.append(f"**Overall Risk Rating:** {executive['overall_risk_rating']}")
            lines.append("")
        if executive.get("summary"):
            lines.append(executive["summary"])
            lines.append("")

    # Metrics
    metrics = report_json.get("metrics", {})
    if metrics and metrics.get("risk_distribution"):
        lines.append("## Risk Summary")
        lines.append("")
        dist = metrics["risk_distribution"]
        lines.append(f"- **Critical:** {dist.get('critical', 0)}")
        lines.append(f"- **High:** {dist.get('high', 0)}")
        lines.append(f"- **Medium:** {dist.get('medium', 0)}")
        lines.append(f"- **Low:** {dist.get('low', 0)}")
        lines.append("")

    # Findings
    findings = report_json.get("findings", [])
    if findings:
        lines.append("## Findings")
        lines.append("")

        for finding in findings:
            fid = finding.get("id", 'F-000')
            title = finding.get("title", 'Untitled Finding')
            severity = finding.get('severity', 'Informational')

            lines.append(f"### {fid} — {title}")
            lines.append("")
            lines.append(f"**Severity:** {severity}")

            if finding.get("category"):
                lines.append(f"**Category:** {finding['category']}")

            if finding.get("domain"):
                lines.append(f"**Domain:** {finding['domain']}")

            if finding.get("summary"):
                lines.append("")
                lines.append(finding["summary"])

            # Risk score
            risk = finding.get("risk", {})
            if risk and risk.get("score"):
                lines.append("")
                lines.append(f"**Risk Score:** {risk['score']}")

            lines.append("")

    # Recommendations
    recommendations = report_json.get("recommendations", [])
    if recommendations:
        lines.append("## Recommendations")
        lines.append("")

        for rec in recommendations:
            rid = rec.get("id", 'REC-000')
            title = rec.get("title", "Untitled Recommendation")
            priority = rec.get("priority", "Medium")

            lines.append(f"### {rid} — {title}")
            lines.append("")
            lines.append(f"**Priority:** {priority}")

            if rec.get("summary"):
                lines.append("")
                lines.append(rec["summary"])

            lines.append("")

    # Evidence
    evidence = report_json.get("evidence", [])
    if evidence:
        lines.append("## Evidence")
        lines.append("")

        for item in evidence:
            eid = item.get("id", 'E-000')
            title = item.get("title", "Untitled Evidence")

            lines.append(f"### {eid} — {title}")

            if item.get("type"):
                lines.append(f"**Type:** {item['type']}")

            if item.get("summary"):
                lines.append("")
                lines.append(item["summary"])

            lines.append("")

    return "\n".join(lines)


def export_html(
    report_json: Dict[str, Any],
    *,
    template: Optional[str] = None,
    theme: Optional[str] = None,
    inline_css: bool = True,
) -> str:
    """Export report to HTML format.

    Args:
        report_json: The report JSON
        template: Optional template name
        theme: Optional theme profile
        inline_css: Whether to inline CSS

    Returns:
        HTML string
    """
    try:
        if template == "professional":
            html = render_professional_html(report_json, theme_profile=theme or "vistiqx_consulting")
        else:
            html = render_report_html(report_json, template_name=template, theme_profile=theme)

        if inline_css:
            # For standalone HTML files, CSS is already inline in templates
            pass

        return html

    except Exception as e:
        raise ExportError(f"HTML export failed: {e}")


def export_csv(report_json: Dict[str, Any]) -> str:
    """Export findings to CSV format.

    Args:
        report_json: The report JSON

    Returns:
        CSV string
    """
    findings = report_json.get("findings", [])

    if not findings:
        return "ID,Title,Severity,Category,Summary,Risk Score\n"

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["ID", "Title", "Severity", "Category", "Summary", "Risk Score"])

    # Data rows
    for finding in findings:
        risk_score = finding.get("risk", {}).get("score", "")
        writer.writerow([
            finding.get("id", ""),
            finding.get("title", ""),
            finding.get("severity", ""),
            finding.get("category", ""),
            finding.get("summary", ""),
            risk_score,
        ])

    return output.getvalue()


def export_pdf(
    report_json: Dict[str, Any],
    *,
    template: Optional[str] = None,
    theme: Optional[str] = None,
) -> str:
    """Export report to PDF format.

    Args:
        report_json: The report JSON
        template: Optional template name
        theme: Optional theme profile

    Returns:
        Path to generated PDF file
    """
    try:
        # Generate HTML first
        if template == "professional":
            html = render_professional_html(report_json, theme_profile=theme or "vistiqx_consulting")
        else:
            html = render_report_html(report_json, template_name=template, theme_profile=theme)

        # Create temp PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            pdf_path = tmp.name

        # Render PDF
        render_pdf_from_html(html, pdf_path)

        return pdf_path

    except Exception as e:
        raise ExportError(f"PDF export failed: {e}")


def batch_export(
    report_json: Dict[str, Any],
    formats: List[str],
    *,
    template: Optional[str] = None,
    theme: Optional[str] = None,
) -> Dict[str, str]:
    """Export report to multiple formats.

    Args:
        report_json: The report JSON
        formats: List of formats to export
        template: Optional template name
        theme: Optional theme profile

    Returns:
        Dictionary mapping format to export result
    """
    results = {}

    for fmt in formats:
        try:
            result = export_report(
                report_json,
                fmt,
                template=template,
                theme=theme,
            )
            results[fmt] = result
        except Exception as e:
            results[fmt] = f"ERROR: {e}"

    return results
