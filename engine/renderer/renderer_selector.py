"""Renderer selector for Metis Report Engine.

This module provides schema version detection and automatic renderer/template
selection based on the report's schema_version field.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple
from pathlib import Path


logger = logging.getLogger(__name__)


# Renderer configuration by schema version
RENDERER_CONFIG = {
    "1": {
        "renderer": "legacy",
        "template": "report_template.html",
        "theme": "default",
        "description": "Legacy minimal renderer",
    },
    "2": {
        "renderer": "consulting",
        "template": "consulting/consulting_report_template.html",
        "theme": "vistiqx_consulting",
        "description": "Consulting-grade renderer with full sections",
    },
    "2.0": {
        "renderer": "consulting",
        "template": "consulting/consulting_report_template.html",
        "theme": "vistiqx_consulting",
        "description": "Consulting-grade renderer with full sections",
    },
}


def detect_schema_version(report: Dict[str, Any]) -> str:
    """Detect the schema version from a report.
    
    Args:
        report: The report JSON
        
    Returns:
        Schema version string (e.g., "1", "2", "2.0")
        
    Detection priority:
    1. Explicit schema_version field
    2. Report structure inference
    3. Default to "1" for backward compatibility
    """
    # Check for explicit schema_version at root
    schema_version = report.get("schema_version")
    if schema_version:
        version_str = str(schema_version)
        # Normalize "2.0" to "2" for lookup
        if version_str.startswith("2"):
            return "2"
        return version_str
    
    # Infer from structure: v2 has report.sections array
    report_data = report.get("report", {})
    if isinstance(report_data, dict) and "sections" in report_data:
        sections = report_data.get("sections", [])
        if isinstance(sections, list) and len(sections) > 0:
            logger.info("Inferred schema version 2 from report.sections structure")
            return "2"
    
    # Default to v1 for backward compatibility
    logger.info("No schema_version found, defaulting to version 1")
    return "1"


def select_renderer(report: Dict[str, Any]) -> Dict[str, Any]:
    """Select the appropriate renderer and template for a report.
    
    Args:
        report: The report JSON
        
    Returns:
        Dictionary with renderer configuration:
        - schema_version: detected version
        - renderer: renderer type name
        - template: template path
        - theme: theme profile
        - description: human-readable description
    """
    version = detect_schema_version(report)
    config = RENDERER_CONFIG.get(version, RENDERER_CONFIG["1"])
    
    result = {
        "schema_version": version,
        "renderer": config["renderer"],
        "template": config["template"],
        "theme": config["theme"],
        "description": config["description"],
    }
    
    logger.info(
        f"Renderer selection: version={version}, renderer={config['renderer']}, "
        f"template={config['template']}"
    )
    
    return result


def should_use_consulting_renderer(report: Dict[str, Any]) -> bool:
    """Check if the consulting renderer should be used.
    
    Args:
        report: The report JSON
        
    Returns:
        True if consulting renderer should be used
    """
    version = detect_schema_version(report)
    return version.startswith("2")


def log_render_selection(
    report: Dict[str, Any],
    renderer_config: Dict[str, Any],
    sections_count: int = 0,
    visualizations_count: int = 0,
    charts_generated: int = 0,
) -> None:
    """Log detailed render path information.
    
    Args:
        report: The report JSON
        renderer_config: Renderer configuration from select_renderer()
        sections_count: Number of sections rendered
        visualizations_count: Number of visualization blocks
        charts_generated: Number of charts actually generated
    """
    report_id = report.get("report", {}).get("id", "unknown")
    report_title = report.get("report", {}).get("title", "Untitled")
    
    logger.info("=" * 60)
    logger.info("RENDER PATH SELECTION")
    logger.info("=" * 60)
    logger.info(f"Report ID: {report_id}")
    logger.info(f"Report Title: {report_title}")
    logger.info(f"Detected Schema Version: {renderer_config['schema_version']}")
    logger.info(f"Selected Renderer: {renderer_config['renderer']}")
    logger.info(f"Selected Template: {renderer_config['template']}")
    logger.info(f"Selected Theme: {renderer_config['theme']}")
    logger.info(f"Renderer Description: {renderer_config['description']}")
    logger.info(f"Sections Count: {sections_count}")
    logger.info(f"Visualization Blocks: {visualizations_count}")
    logger.info(f"Charts Generated: {charts_generated}")
    logger.info("=" * 60)
