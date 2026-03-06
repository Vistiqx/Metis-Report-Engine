
"""Visualization registry for Metis Report Engine."""

from __future__ import annotations

from typing import Callable, Dict, Any

from engine.visualizations.risk_matrix import render_risk_matrix_svg
from engine.visualizations.svg_charts import (
    render_severity_distribution_svg,
    render_kpi_cards_html,
    render_timeline_svg,
)


VisualizationRenderer = Callable[[Dict[str, Any]], str]


REGISTRY: dict[str, VisualizationRenderer] = {
    "risk_matrix": render_risk_matrix_svg,
    "severity_distribution": render_severity_distribution_svg,
    "kpi_summary_cards": render_kpi_cards_html,
    "timeline": render_timeline_svg,
}


def get_renderer(visualization_type: str) -> VisualizationRenderer:
    """Return a registered visualization renderer."""
    if visualization_type not in REGISTRY:
        raise KeyError(f"Unsupported visualization type: {visualization_type}")
    return REGISTRY[visualization_type]


def list_supported_visualizations() -> list[str]:
    """Return the registered visualization types."""
    return sorted(REGISTRY.keys())
