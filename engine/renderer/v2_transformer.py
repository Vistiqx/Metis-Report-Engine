"""V2 schema to template context transformer for Metis Report Engine.

Transforms schema v2 reports into the format expected by the consulting template,
including proper structure, visualizations, and chart generation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from engine.visualizations.visualization_engine import (
    VisualizationEngine,
    generate_risk_distribution_chart,
    generate_risk_matrix_chart,
    generate_financial_exposure_chart,
    generate_radar_chart,
)


logger = logging.getLogger(__name__)


def transform_v2_to_template_context(report: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
    """Transform a v2 schema report into template rendering context.
    
    Args:
        report: The v2 schema report JSON
        
    Returns:
        Tuple of (template context dictionary, charts_generated count)
    """
    context = {}
    
    # Extract report data - v2 has report as an object with metadata
    report_data = report.get("report", {})
    
    # Check if using new nested metadata structure (v2.0+)
    metadata = report_data.get("metadata", {})
    if metadata:
        # New v2 structure with nested metadata
        context["report"] = {
            "metadata": {
                "id": metadata.get("id", "unknown"),
                "title": metadata.get("title", "Untitled Report"),
                "subtitle": metadata.get("subtitle", ""),
                "type": metadata.get("type", "risk_assessment"),
                "classification": metadata.get("classification", "Confidential"),
                "version": metadata.get("version", "1.0"),
                "date_created": metadata.get("date_created", ""),
                "date_published": metadata.get("date_published") or metadata.get("date_created", ""),
                "client": metadata.get("client", {"name": "Client Organization"}),
                "consultant": metadata.get("consultant", {"name": "Consultant", "firm": "Consulting Firm"}),
            },
            "sections": [],
            "findings": [],
            "recommendations": [],
            "appendices": [],
        }
        
        # Extract findings and recommendations from nested report structure
        findings = report_data.get("findings", [])
        recommendations = report_data.get("recommendations", [])
        appendices = report_data.get("appendices", [])
        exec_summary = report_data.get("executive_summary", {})
        sections = report_data.get("sections", [])
    else:
        # Legacy v2 structure with flat properties
        context["report"] = {
            "metadata": {
                "id": report_data.get("id", "unknown"),
                "title": report_data.get("title", "Untitled Report"),
                "subtitle": report_data.get("subtitle", ""),
                "type": report_data.get("type", "risk_assessment"),
                "classification": report_data.get("classification", "Confidential"),
                "version": report_data.get("version", "1.0"),
                "date_created": report_data.get("date_created", ""),
                "date_published": report_data.get("date_published") or report_data.get("date_created", ""),
                "client": {
                    "name": report_data.get("client", "Client Organization"),
                    "organization": report_data.get("client", ""),
                },
                "consultant": {
                    "name": report_data.get("author", "Consultant"),
                    "firm": report_data.get("author", "Consulting Firm"),
                    "contact": "",
                },
            },
            "sections": [],
            "findings": [],
            "recommendations": [],
            "appendices": [],
        }
        
        # Extract from root level
        findings = report.get("findings", [])
        recommendations = report.get("recommendations", [])
        appendices = report.get("appendices", [])
        exec_summary = report.get("executive_summary", {})
        sections = report_data.get("sections", [])
    
    # Transform executive summary
    if exec_summary:
        context["report"]["executive_summary"] = {
            "overall_risk_rating": exec_summary.get("overall_risk_rating", "Moderate"),
            "summary": exec_summary.get("summary", ""),
            "key_findings": exec_summary.get("key_findings", []) or exec_summary.get("top_risks", []),
            "business_impact": exec_summary.get("business_impact", ""),
            "recommended_actions": exec_summary.get("recommended_actions", "") or exec_summary.get("recommended_action", ""),
            "risk_score": exec_summary.get("risk_score", 0),
        }
    
    # Transform sections
    if sections:
        context["report"]["sections"] = _transform_sections(sections)
    else:
        context["report"]["sections"] = _generate_sections_from_legacy(report)
    
    # Transform findings, recommendations, appendices
    context["report"]["findings"] = [_transform_finding(f) for f in findings]
    context["report"]["recommendations"] = [_transform_recommendation(r) for r in recommendations]
    context["report"]["appendices"] = [_transform_appendix(a) for a in appendices]
    
    # Generate colors for theme
    context["colors"] = {
        "primary": "#4C3D75",
        "secondary": "#6B5B95",
        "accent": "#88B04B",
        "critical": "#E74C3C",
        "high": "#E67E22",
        "moderate": "#F39C12",
        "low": "#27AE60",
        "minimal": "#3498DB",
    }
    
    # Process and generate visualizations
    context["visualizations"] = []
    context["has_visualizations"] = False
    charts_generated = 0
    
    try:
        viz_data = _generate_visualizations(report)
        context["visualizations"] = viz_data
        context["has_visualizations"] = len(viz_data) > 0
        charts_generated = len(viz_data)
        logger.info(f"Generated {charts_generated} visualizations")
    except Exception as e:
        logger.error(f"Failed to generate visualizations: {e}")
    
    # Add chart/matrix blocks to sections
    _inject_charts_into_sections(context["report"]["sections"], context["visualizations"])
    
    logger.info(f"Transformed v2 report: {len(context['report']['sections'])} sections, "
                f"{len(context['report']['findings'])} findings, "
                f"{len(context['report']['recommendations'])} recommendations")
    
    return context, charts_generated


def _transform_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform v2 sections to template format.
    
    Args:
        sections: List of v2 section objects
        
    Returns:
        List of transformed section objects
    """
    transformed = []
    
    for i, section in enumerate(sections):
        transformed_section = {
            "id": section.get("id", f"section-{i}"),
            "title": section.get("title", f"Section {i+1}"),
            "type": section.get("type", "generic"),
            "summary": section.get("summary", ""),
            "order": section.get("order", i),
            "show_in_toc": section.get("show_in_toc", True),
            "blocks": [],
        }
        
        # Transform content blocks
        blocks = section.get("blocks", [])
        for block in blocks:
            transformed_block = _transform_block(block)
            if transformed_block:
                transformed_section["blocks"].append(transformed_block)
        
        transformed.append(transformed_section)
    
    return transformed


def _transform_block(block: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform a content block to template format.
    
    Args:
        block: Content block from v2 schema
        
    Returns:
        Transformed block or None if invalid
    """
    block_type = block.get("type", "paragraph")
    
    if block_type == "paragraph":
        return {
            "type": "paragraph",
            "text": block.get("text", ""),
        }
    
    elif block_type == "bullet_list":
        items = block.get("items", [])
        # Ensure items is a list, not a method or other type
        if not isinstance(items, list):
            items = []
        return {
            "type": "bullet_list",
            "items_list": items,  # Use different key to avoid conflict with dict.items()
        }
    
    elif block_type == "numbered_list":
        items = block.get("items", [])
        # Ensure items is a list, not a method or other type
        if not isinstance(items, list):
            items = []
        return {
            "type": "numbered_list",
            "items_list": items,  # Use different key to avoid conflict with dict.items()
        }
    
    elif block_type == "table":
        table_data = block.get("table", {})
        return {
            "type": "table",
            "title": block.get("title", ""),
            "table": {
                "headers": table_data.get("headers", []),
                "rows": table_data.get("rows", []),
            },
        }
    
    elif block_type == "chart":
        chart_data = block.get("chart", {})
        return {
            "type": "chart",
            "title": block.get("title", chart_data.get("title", "Chart")),
            "chart": chart_data,
        }
    
    elif block_type == "callout":
        callout_data = block.get("callout", {})
        return {
            "type": "callout",
            "callout": {
                "type": callout_data.get("type", "info"),
                "title": callout_data.get("title", ""),
                "content": callout_data.get("content", ""),
            },
        }
    
    elif block_type == "key_metrics":
        return {
            "type": "key_metrics",
            "title": block.get("title", "Key Metrics"),
        }
    
    return None


def _transform_finding(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a finding to consulting template format.
    
    Args:
        finding: Finding object from report
        
    Returns:
        Transformed finding object
    """
    risk_data = finding.get("risk", {})
    
    return {
        "id": finding.get("id", "F-000"),
        "title": finding.get("title", finding.get("short_title", "Untitled Finding")),
        "description": finding.get("description", finding.get("summary", "")),
        "severity": finding.get("severity", "Medium"),
        "category": finding.get("category", "General"),
        "likelihood": risk_data.get("likelihood", finding.get("likelihood", 3)),
        "impact": risk_data.get("impact", finding.get("impact", 3)),
        "risk_score": risk_data.get("score", finding.get("risk_score", 0)),
    }


def _transform_recommendation(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a recommendation to consulting template format.
    
    Args:
        rec: Recommendation object from report
        
    Returns:
        Transformed recommendation object
    """
    return {
        "id": rec.get("id", "REC-000"),
        "title": rec.get("title", rec.get("short_title", "Untitled Recommendation")),
        "description": rec.get("description", rec.get("action", {}).get("description", rec.get("summary", ""))),
        "priority": rec.get("priority", "Medium"),
        "effort": rec.get("implementation", {}).get("effort", "Medium"),
        "timeline": rec.get("recommended_timeline", rec.get("timeline", "TBD")),
    }


def _transform_appendix(appendix: Dict[str, Any]) -> Dict[str, Any]:
    """Transform an appendix to consulting template format.
    
    Args:
        appendix: Appendix object from report
        
    Returns:
        Transformed appendix object
    """
    return {
        "id": appendix.get("id", ""),
        "title": appendix.get("title", "Appendix"),
        "content": appendix.get("content", ""),
        "blocks": [_transform_block(b) for b in appendix.get("blocks", []) if _transform_block(b)],
    }


def _generate_sections_from_legacy(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate v2-style sections from legacy v1 report structure.
    
    Args:
        report: Legacy report JSON
        
    Returns:
        List of section objects
    """
    sections = []
    order = 0
    
    # Add methodology section if engagement data exists
    engagement = report.get("engagement", {})
    if engagement:
        sections.append({
            "id": "methodology",
            "title": "Methodology",
            "type": "methodology",
            "summary": "Approach and scope of the assessment",
            "order": order,
            "show_in_toc": True,
            "blocks": [
                {
                    "type": "paragraph",
                    "text": engagement.get("scope_summary", "Assessment conducted per standard methodology."),
                },
                {
                    "type": "bullet_list",
                    "items": [f"Jurisdiction: {j}" for j in engagement.get("jurisdictions", [])] or ["Assessment scope defined"],
                },
            ],
        })
        order += 1
    
    # Add risk analysis section if findings exist
    findings = report.get("findings", [])
    if findings:
        sections.append({
            "id": "risk-analysis",
            "title": "Risk Analysis",
            "type": "risk_analysis",
            "summary": "Detailed analysis of identified risks",
            "order": order,
            "show_in_toc": True,
            "blocks": [
                {
                    "type": "paragraph",
                    "text": f"This assessment identified {len(findings)} significant risk(s) requiring attention.",
                },
            ],
        })
        order += 1
    
    # Add recommendations section
    recommendations = report.get("recommendations", [])
    if recommendations:
        sections.append({
            "id": "recommendations",
            "title": "Strategic Recommendations",
            "type": "recommendations",
            "summary": "Recommended actions to address identified risks",
            "order": order,
            "show_in_toc": True,
            "blocks": [
                {
                    "type": "paragraph",
                    "text": f"The following {len(recommendations)} recommendation(s) are provided to mitigate identified risks.",
                },
            ],
        })
        order += 1
    
    return sections


def _generate_visualizations(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate visualization data from report.
    
    Args:
        report: Report JSON with metrics and risk data
        
    Returns:
        List of visualization objects with rendered SVG data
    """
    visualizations = []
    
    # Get metrics
    metrics = report.get("metrics", {})
    risk_distribution = metrics.get("risk_distribution", {})
    financial_exposure = metrics.get("financial_exposure", {})
    
    # Generate risk distribution chart
    if risk_distribution and any(risk_distribution.values()):
        try:
            # Convert to proper format
            dist_data = {}
            for key, value in risk_distribution.items():
                # Capitalize first letter
                formatted_key = key.capitalize() if key else "Unknown"
                dist_data[formatted_key] = value
            
            svg_data = generate_risk_distribution_chart(
                dist_data,
                title="Risk Distribution"
            )
            
            visualizations.append({
                "id": "viz-risk-distribution",
                "type": "risk_distribution",
                "title": "Risk Distribution",
                "rendered": svg_data,
                "chart": {
                    "svg_data": svg_data,
                    "chart_type": "donut",
                    "title": "Risk Distribution",
                },
            })
            logger.info("Generated risk distribution chart")
        except Exception as e:
            logger.error(f"Failed to generate risk distribution chart: {e}")
    
    # Generate risk matrix if risk model exists
    risk_model = report.get("risk_model", {})
    matrix_items = risk_model.get("matrix", [])
    if matrix_items:
        try:
            # Convert matrix items to expected format
            items = []
            for item in matrix_items:
                items.append({
                    "id": item.get("risk_id", "R"),
                    "likelihood": item.get("likelihood", 3),
                    "impact": item.get("impact", 3),
                    "severity": item.get("severity", "Moderate"),
                })
            
            svg_data = generate_risk_matrix_chart(
                items,
                title="Risk Matrix"
            )
            
            visualizations.append({
                "id": "viz-risk-matrix",
                "type": "risk_matrix",
                "title": "Risk Matrix",
                "rendered": svg_data,
                "chart": {
                    "svg_data": svg_data,
                    "chart_type": "matrix",
                    "title": "Risk Matrix",
                },
            })
            logger.info("Generated risk matrix chart")
        except Exception as e:
            logger.error(f"Failed to generate risk matrix chart: {e}")
    
    # Generate financial exposure chart if data exists
    if financial_exposure:
        try:
            scenarios = [
                {
                    "name": "Minimum",
                    "min": 0,
                    "max": financial_exposure.get("minimum", 0),
                },
                {
                    "name": "Maximum",
                    "min": 0,
                    "max": financial_exposure.get("maximum", 0),
                },
            ]
            
            svg_data = generate_financial_exposure_chart(
                scenarios,
                title="Financial Exposure"
            )
            
            visualizations.append({
                "id": "viz-financial-exposure",
                "type": "financial_exposure",
                "title": "Financial Exposure",
                "rendered": svg_data,
                "chart": {
                    "svg_data": svg_data,
                    "chart_type": "bar",
                    "title": "Financial Exposure",
                },
            })
            logger.info("Generated financial exposure chart")
        except Exception as e:
            logger.error(f"Failed to generate financial exposure chart: {e}")
    
    return visualizations


def _inject_charts_into_sections(sections: List[Dict[str, Any]], visualizations: List[Dict[str, Any]]) -> None:
    """Inject generated chart blocks into appropriate sections.
    
    Args:
        sections: List of section objects to modify
        visualizations: List of generated visualizations
    """
    if not visualizations:
        return
    
    # Find executive summary or first section
    target_section = None
    for section in sections:
        if section.get("type") == "executive_summary" or "executive" in section.get("title", "").lower():
            target_section = section
            break
    
    # If no executive section found, use first section
    if not target_section and sections:
        target_section = sections[0]
    
    if target_section:
        # Inject chart blocks at the beginning of blocks list
        for viz in visualizations:
            chart_block = {
                "type": "chart",
                "title": viz.get("title", "Chart"),
                "chart": viz.get("chart", {}),
            }
            target_section["blocks"].insert(0, chart_block)
        
        logger.info(f"Injected {len(visualizations)} charts into section: {target_section.get('title', 'Unknown')}")
