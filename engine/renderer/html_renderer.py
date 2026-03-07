"""Enhanced HTML renderer with template and theme support for Metis Report Engine.

This module provides flexible HTML rendering with:
- Multiple template support
- Theme profile selection
- Visualization injection
- Table of contents generation
- Schema version detection with automatic renderer selection
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from jinja2 import Environment, FileSystemLoader, select_autoescape

from engine.visualizations.chart_registry import get_renderer
from engine.renderer.toc_generator import build_toc
from engine.renderer.renderer_selector import (
    detect_schema_version,
    select_renderer,
    log_render_selection,
)
from engine.renderer.v2_transformer import transform_v2_to_template_context


logger = logging.getLogger(__name__)


def render_report_html(
    payload: Dict[str, Any],
    template_name: Optional[str] = None,
    theme_profile: Optional[str] = None,
) -> str:
    """Render report to HTML with template and theme selection.

    Args:
        payload: The canonical report JSON
        template_name: Template to use (default: auto-detected based on schema version)
        theme_profile: Theme profile name (default: auto-detected based on schema version)

    Returns:
        Rendered HTML string
    """
    template_root = Path(__file__).resolve().parents[2] / "templates"

    env = Environment(
        loader=FileSystemLoader(str(template_root)),
        autoescape=select_autoescape(["html", "xml"])
    )

    # Detect schema version and select appropriate renderer/template
    schema_version = detect_schema_version(payload)
    renderer_config = select_renderer(payload)
    
    # Log the render path selection
    logger.info(f"[RENDER] Schema version detected: {schema_version}")
    logger.info(f"[RENDER] Selected renderer: {renderer_config['renderer']}")
    logger.info(f"[RENDER] Selected template: {renderer_config['template']}")
    
    # Determine template and theme
    if template_name:
        # User explicitly specified template, use it
        template_id = template_name
        actual_theme = theme_profile or renderer_config["theme"]
        logger.info(f"[RENDER] Using explicit template: {template_id}")
    else:
        # Auto-select based on schema version
        template_id = renderer_config["template"]
        actual_theme = theme_profile or renderer_config["theme"]
        logger.info(f"[RENDER] Auto-selected template for schema v{schema_version}: {template_id}")
    
    # Prepare rendering context based on schema version
    if schema_version.startswith("2"):
        # Use v2 transformer for consulting-grade rendering
        logger.info("[RENDER] Using v2 transformer for context preparation")
        context, charts_generated = transform_v2_to_template_context(payload)
        
        # Log render details
        sections_count = len(context.get("report", {}).get("sections", []))
        viz_count = len(context.get("visualizations", []))
        log_render_selection(
            payload,
            renderer_config,
            sections_count=sections_count,
            visualizations_count=viz_count,
            charts_generated=charts_generated,
        )
    else:
        # Use legacy context preparation for v1
        logger.info("[RENDER] Using legacy context preparation for schema v1")
        context = _prepare_render_context(payload, actual_theme)
        sections_count = 0
        viz_count = len(context.get("visualizations", []))
        charts_generated = 0
        
        log_render_selection(
            payload,
            renderer_config,
            sections_count=sections_count,
            visualizations_count=viz_count,
            charts_generated=charts_generated,
        )
    
    # Load template
    template = env.get_template(template_id)
    
    logger.info(f"[RENDER] Rendering template: {template_id}")
    html = template.render(**context)
    logger.info(f"[RENDER] HTML generation complete: {len(html)} bytes")
    
    return html


def _prepare_render_context(
    payload: Dict[str, Any],
    theme_profile: Optional[str] = None,
) -> Dict[str, Any]:
    """Prepare the rendering context with visualizations and theme.

    Args:
        payload: The report JSON
        theme_profile: Optional theme profile name

    Returns:
        Enhanced context dictionary
    """
    context = dict(payload)

    # Load theme profile
    profile_name = theme_profile or payload.get("report", {}).get("theme_profile", "default")
    context["theme"] = _load_theme_profile(profile_name)

    # Render visualizations
    visualizations = payload.get("visualizations", [])
    rendered_viz = []
    for viz in visualizations:
        try:
            viz_type = viz.get("type")
            data_source = viz.get("data_source", "")

            # Get data from the appropriate source
            data = _resolve_data_source(payload, data_source)

            # Render the visualization
            renderer = get_renderer(viz_type)
            rendered = renderer(data)

            rendered_viz.append({
                **viz,
                "rendered": rendered,
            })
        except (KeyError, ValueError) as e:
            # Log error but continue rendering
            rendered_viz.append({
                **viz,
                "rendered": f"<!-- Failed to render {viz.get('type', 'unknown')}: {e} -->",
            })

    context["visualizations"] = rendered_viz
    context["has_visualizations"] = len(rendered_viz) > 0

    # Generate table of contents
    context["toc"] = build_toc([])

    return context


def _load_theme_profile(profile_name: str) -> Dict[str, Any]:
    """Load theme profile configuration.

    Args:
        profile_name: Name of the theme profile

    Returns:
        Theme profile dictionary
    """
    profiles_root = Path(__file__).resolve().parents[2] / "theme" / "client_profiles"
    profile_path = profiles_root / f"{profile_name}.json"

    # Try to load the profile
    if profile_path.exists():
        with profile_path.open("r", encoding="utf-8") as f:
            profile = json.load(f)
    else:
        # Fall back to default
        with (profiles_root / "default.json").open("r", encoding="utf-8") as f:
            profile = json.load(f)

    # Load base colors
    colors_path = Path(__file__).resolve().parents[2] / "theme" / "colors.json"
    with colors_path.open("r", encoding="utf-8") as f:
        colors = json.load(f)

    # Load typography
    typography_path = Path(__file__).resolve().parents[2] / "theme" / "typography.json"
    with typography_path.open("r", encoding="utf-8") as f:
        typography = json.load(f)

    return {
        "profile": profile,
        "colors": colors,
        "typography": typography,
    }


def _resolve_data_source(payload: Dict[str, Any], data_source: str) -> Dict[str, Any]:
    """Resolve a data source path to actual data.

    Args:
        payload: The report JSON
        data_source: Dot-notation path to data (e.g., "metrics.risk_distribution")

    Returns:
        Data at the specified path
    """
    if not data_source:
        return payload

    parts = data_source.split(".")
    data = payload

    for part in parts:
        if isinstance(data, dict) and part in data:
            data = data[part]
        else:
            # Return empty dict if path not found
            return {}

    return data if isinstance(data, dict) else {"value": data}


def render_preview_html(
    payload: Dict[str, Any],
    theme_profile: Optional[str] = None,
) -> str:
    """Render a preview HTML with minimal styling for quick viewing.

    Args:
        payload: The report JSON
        theme_profile: Optional theme profile

    Returns:
        Rendered HTML string
    """
    return render_report_html(
        payload,
        template_name="report_template.html",
        theme_profile=theme_profile,
    )


def render_professional_html(
    payload: Dict[str, Any],
    theme_profile: str = "vistiqx_consulting",
) -> str:
    """Render a professional consulting-style HTML.

    Args:
        payload: The report JSON
        theme_profile: Theme profile to use (default: vistiqx_consulting)

    Returns:
        Rendered HTML string
    """
    return render_report_html(
        payload,
        template_name="professional_consulting_report.html",
        theme_profile=theme_profile,
    )
