"""SVG chart generators for Metis Report Engine.

This module provides deterministic visualization generation for reports.
All charts use theme tokens from chart_tokens.json for consistent styling.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _load_chart_tokens() -> Dict[str, str]:
    """Load chart color tokens from theme."""
    tokens_path = Path(__file__).resolve().parents[2] / "theme" / "chart_tokens.json"
    if tokens_path.exists():
        with tokens_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "critical_color": "#AC8FFE",
        "high_color": "#8A6FD6",
        "medium_color": "#CFC4F7",
        "low_color": "#E8E8F8",
        "informational_color": "#D9D9E6",
        "axis_color": "#4C3D75",
        "text_color": "#121212",
        "muted_text_color": "#6E6E80",
        "gridline_color": "#D7CFFC"
    }


def render_severity_distribution_svg(data: Dict[str, Any]) -> str:
    """Render a severity distribution bar chart as SVG.
    
    Args:
        data: Dictionary with 'critical', 'high', 'medium', 'low' counts
        
    Returns:
        SVG string representation of the chart
    """
    tokens = _load_chart_tokens()
    
    critical = int(data.get("critical", 0))
    high = int(data.get("high", 0))
    medium = int(data.get("medium", 0))
    low = int(data.get("low", 0))
    
    max_value = max(critical, high, medium, low, 1)
    
    colors = {
        "critical": tokens.get("critical_color", "#AC8FFE"),
        "high": tokens.get("high_color", "#8A6FD6"),
        "medium": tokens.get("medium_color", "#CFC4F7"),
        "low": tokens.get("low_color", "#E8E8F8"),
    }
    
    text_color = tokens.get("text_color", "#121212")
    
    def bar(x: int, value: int, label: str, color: str) -> str:
        height = int((value / max_value) * 120)
        y = 140 - height
        return (
            f'<g>'
            f'<rect x="{x}" y="{y}" width="40" height="{height}" rx="6" fill="{color}"></rect>'
            f'<text x="{x+20}" y="160" text-anchor="middle" fill="{text_color}">{label}</text>'
            f'<text x="{x+20}" y="{y-6}" text-anchor="middle" fill="{text_color}">{value}</text>'
            f'</g>'
        )
    
    return (
        '<svg viewBox="0 0 260 180" xmlns="http://www.w3.org/2000/svg">'
        f'<style>text{{font-family:Inter,Arial,sans-serif;font-size:12px;}}</style>'
        f'{bar(20, critical, "C", colors["critical"])}'
        f'{bar(80, high, "H", colors["high"])}'
        f'{bar(140, medium, "M", colors["medium"])}'
        f'{bar(200, low, "L", colors["low"])}'
        '</svg>'
    )


def render_kpi_cards_html(data: Dict[str, Any]) -> str:
    """Render KPI summary cards as HTML.
    
    Args:
        data: Dictionary containing metrics and executive summary data
        
    Returns:
        HTML string with styled KPI cards
    """
    tokens = _load_chart_tokens()
    text_color = tokens.get("text_color", "#121212")
    accent_color = tokens.get("critical_color", "#AC8FFE")
    
    # Extract KPI values from various data sources
    kpis = []
    
    # From executive_summary.key_statistics if available
    exec_summary = data.get("executive_summary", {})
    if isinstance(exec_summary, dict):
        key_stats = exec_summary.get("key_statistics", {})
        if isinstance(key_stats, dict):
            for key, value in key_stats.items():
                kpis.append({
                    "label": key.replace("_", " ").title(),
                    "value": str(value),
                })
    
    # From metrics.risk_distribution
    metrics = data.get("metrics", {})
    if isinstance(metrics, dict):
        risk_dist = metrics.get("risk_distribution", {})
        if isinstance(risk_dist, dict) and not any(k in [k["label"].lower().replace(" ", "_") for k in kpis] for k in ["critical", "high", "medium", "low"]):
            total = sum(risk_dist.get(k, 0) for k in ["critical", "high", "medium", "low"])
            if total > 0:
                kpis.insert(0, {"label": "Total Findings", "value": str(total)})
    
    # Generate cards HTML
    cards_html = []
    for kpi in kpis[:4]:  # Limit to 4 cards
        card = (
            f'<div class="kpi-card" style="'
            f'background: linear-gradient(135deg, rgba(172,143,254,.16), rgba(138,111,214,.10));'
            f'border: 1px solid rgba(76,61,117,.16);'
            f'border-radius: 18px;'
            f'padding: 18px;'
            f'text-align: center;'
            f'box-shadow: 0 10px 24px rgba(18,18,18,.05);'
            f'">'
            f'<div style="font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: {tokens.get("axis_color", "#4C3D75")}; margin-bottom: 8px;">{kpi["label"]}</div>'
            f'<div style="font-size: 28px; font-weight: 700; color: {accent_color};">{kpi["value"]}</div>'
            f'</div>'
        )
        cards_html.append(card)
    
    if not cards_html:
        # Return empty state card
        cards_html.append(
            f'<div style="'
            f'background: {tokens.get("low_color", "#E8E8F8")};'
            f'border-radius: 12px;'
            f'padding: 24px;'
            f'text-align: center;'
            f'color: {tokens.get("muted_text_color", "#6E6E80")};'
            f'">No metrics available</div>'
        )
    
    grid_style = (
        f'display: grid;'
        f'grid-template-columns: repeat({min(len(cards_html), 2)}, 1fr);'
        f'gap: 16px;'
    )
    
    return f'<div style="{grid_style}">{"".join(cards_html)}</div>'


def render_timeline_svg(data: Dict[str, Any]) -> str:
    """Render a timeline visualization as SVG.
    
    Args:
        data: Dictionary containing recommendations with timeline data
        
    Returns:
        SVG string representation of the timeline
    """
    tokens = _load_chart_tokens()
    
    # Extract timeline items from recommendations
    items = []
    recommendations = data.get("recommendations", [])
    
    if isinstance(recommendations, list):
        for rec in recommendations:
            if isinstance(rec, dict):
                item = {
                    "id": rec.get("id", "UNKNOWN"),
                    "title": rec.get("title", "Untitled"),
                    "timeline": rec.get("recommended_timeline", "TBD"),
                    "priority": rec.get("priority", "Medium"),
                }
                items.append(item)
    
    if not items:
        # Return empty timeline
        return (
            '<svg viewBox="0 0 600 100" xmlns="http://www.w3.org/2000/svg">'
            f'<text x="300" y="50" text-anchor="middle" fill="{tokens.get("muted_text_color", "#6E6E80")}" font-family="Inter,Arial,sans-serif">No timeline data available</text>'
            '</svg>'
        )
    
    # Sort by priority
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    items.sort(key=lambda x: priority_order.get(x["priority"], 4))
    
    # SVG dimensions
    width = 600
    item_height = 60
    height = max(120, len(items) * item_height + 40)
    
    colors = {
        "Critical": tokens.get("critical_color", "#AC8FFE"),
        "High": tokens.get("high_color", "#8A6FD6"),
        "Medium": tokens.get("medium_color", "#CFC4F7"),
        "Low": tokens.get("low_color", "#E8E8F8"),
    }
    
    text_color = tokens.get("text_color", "#121212")
    muted_color = tokens.get("muted_text_color", "#6E6E80")
    
    # Build timeline
    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        f'<style>text{{font-family:Inter,Arial,sans-serif;}}</style>',
    ]
    
    # Timeline line
    parts.append(f'<line x1="30" y1="30" x2="30" y2="{height - 30}" stroke="{tokens.get("axis_color", "#4C3D75")}" stroke-width="2"/>')
    
    for i, item in enumerate(items):
        y = 30 + i * item_height
        color = colors.get(item["priority"], colors["Medium"])
        
        # Timeline node
        parts.append(f'<circle cx="30" cy="{y}" r="8" fill="{color}"/>')
        
        # Item text
        parts.append(f'<text x="50" y="{y + 4}" font-size="14" font-weight="600" fill="{text_color}">{item["id"]} — {item["title"][:40]}{"..." if len(item["title"]) > 40 else ""}</text>')
        
        # Timeline text
        parts.append(f'<text x="50" y="{y + 20}" font-size="12" fill="{muted_color}">Timeline: {item["timeline"]}</text>')
    
    parts.append('</svg>')
    return "".join(parts)


# Backward compatibility alias
severity_distribution_svg = render_severity_distribution_svg
