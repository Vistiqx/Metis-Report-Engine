
"""Visualization resolver for Metis Report Engine."""

from __future__ import annotations

from typing import Any, Dict, List


def resolve_visualizations(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Resolve default visualization set based on available report data."""
    visualizations: List[Dict[str, Any]] = []

    metrics = report.get("metrics", {})
    risk_model = report.get("risk_model", {})
    findings = report.get("findings", [])

    if metrics.get("risk_distribution"):
        visualizations.append(
            {
                "id": "V-001",
                "type": "severity_distribution",
                "title": "Severity Distribution",
                "data_source": "metrics.risk_distribution",
                "style_variant": "executive",
            }
        )

    if risk_model.get("matrix") or has_matrix_inputs(findings):
        visualizations.append(
            {
                "id": "V-002",
                "type": "risk_matrix",
                "title": "Likelihood vs Impact",
                "data_source": "risk_model.matrix",
                "style_variant": "executive",
            }
        )

    if report.get("executive_summary") or metrics:
        visualizations.append(
            {
                "id": "V-003",
                "type": "kpi_summary_cards",
                "title": "Executive Summary Metrics",
                "data_source": "executive_summary",
                "style_variant": "executive",
            }
        )

    recommendations = report.get("recommendations", [])
    if recommendations:
        visualizations.append(
            {
                "id": "V-004",
                "type": "timeline",
                "title": "Recommendation Timeline",
                "data_source": "recommendations",
                "style_variant": "operational",
            }
        )

    return visualizations


def has_matrix_inputs(findings: List[Dict[str, Any]]) -> bool:
    """Return True if findings support a matrix view."""
    for finding in findings:
        if finding.get("likelihood") is not None and finding.get("impact") is not None:
            return True
    return False
