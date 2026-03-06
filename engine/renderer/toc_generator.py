
"""Table of contents generator for report sections."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def build_toc(sections: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build table of contents from a list of sections."""
    toc = []
    for index, section in enumerate(sections, start=1):
        toc.append({
            "index": index,
            "title": section.get("title", f"Section {index}"),
            "anchor": section.get("anchor", f"section-{index}"),
            "page_hint": section.get("page_hint"),
        })
    return toc


def generate_toc(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate table of contents from a report.
    
    Args:
        report: The report JSON
        
    Returns:
        List of ToC entries
    """
    sections = []
    
    # Add executive summary
    if report.get("executive_summary"):
        sections.append({
            "title": "Executive Summary",
            "anchor": "executive-summary",
        })
    
    # Add visualizations section if present
    if report.get("visualizations"):
        sections.append({
            "title": "Visual Summary",
            "anchor": "visual-summary",
        })
    
    # Add findings section
    if report.get("findings"):
        sections.append({
            "title": "Findings",
            "anchor": "findings",
        })
    
    # Add recommendations section
    if report.get("recommendations"):
        sections.append({
            "title": "Recommendations",
            "anchor": "recommendations",
        })
    
    # Add evidence section
    if report.get("evidence"):
        sections.append({
            "title": "Evidence",
            "anchor": "evidence",
        })
    
    # Add appendices section
    if report.get("appendices"):
        sections.append({
            "title": "Appendices",
            "anchor": "appendices",
        })
    
    return build_toc(sections)
