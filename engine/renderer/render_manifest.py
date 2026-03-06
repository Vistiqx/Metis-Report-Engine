
"""Render manifest helper for Metis Report Engine.

Produces deterministic metadata about a render operation so reports can be
audited, traced, and later ingested into Metis with full context.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional


DEFAULT_SCHEMA_VERSION = "v1.0.0"
DEFAULT_DSL_SCHEMA_VERSION = "v1.0.0"


def build_render_manifest(
    report_json: Dict[str, Any],
    *,
    report_type: Optional[str] = None,
    template_id: str = "default",
    theme_profile: str = "default",
    validation_status: str = "unknown",
    output_html_path: Optional[str] = None,
    output_pdf_path: Optional[str] = None,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
    dsl_schema_version: str = DEFAULT_DSL_SCHEMA_VERSION,
    render_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a structured manifest for a render event."""
    report = report_json.get("report", {}) if isinstance(report_json, dict) else {}
    visualizations = report_json.get("visualizations", []) if isinstance(report_json, dict) else []

    manifest = {
        "report_id": report.get("id", "UNKNOWN"),
        "title": report.get("title", "Untitled Report"),
        "report_type": report_type or report.get("report_type", "unknown"),
        "schema_version": schema_version,
        "dsl_schema_version": dsl_schema_version,
        "template_id": template_id,
        "theme_profile": theme_profile,
        "rendered_at": _utc_now_iso(),
        "validation_status": validation_status,
        "visualizations": _extract_visualization_types(visualizations),
        "counts": {
            "findings": len(report_json.get("findings", [])),
            "evidence": len(report_json.get("evidence", [])),
            "recommendations": len(report_json.get("recommendations", [])),
            "visualizations": len(visualizations),
        },
        "output_files": {
            "html": output_html_path,
            "pdf": output_pdf_path,
        },
        "render_options": render_options or {},
    }
    return manifest


def _extract_visualization_types(visualizations: Iterable[Dict[str, Any]]) -> list[str]:
    types: list[str] = []
    for item in visualizations:
        vtype = item.get("type")
        if vtype:
            types.append(str(vtype))
    return types


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
