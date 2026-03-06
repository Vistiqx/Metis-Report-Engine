
"""Finding expansion for Metis Report Engine."""

from __future__ import annotations

from typing import Any, Dict, List


def expand_findings(
    findings: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]] | None = None,
    recommendations: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    """Expand findings into a richer internal representation.

    This resolves evidence/recommendation link summaries and calculates
    basic risk metadata where possible.
    """
    evidence = evidence or []
    recommendations = recommendations or []

    evidence_by_id = {item.get("id"): item for item in evidence}
    recommendations_by_id = {item.get("id"): item for item in recommendations}

    expanded: List[Dict[str, Any]] = []
    for finding in findings:
        item = dict(finding)

        likelihood = item.get("likelihood")
        impact = item.get("impact")
        if likelihood is not None and impact is not None:
            item["risk"] = {
                "likelihood": likelihood,
                "impact": impact,
                "score": likelihood * impact,
            }

        item["resolved_evidence"] = [
            evidence_by_id[ref]
            for ref in item.get("evidence_refs", [])
            if ref in evidence_by_id
        ]

        item["resolved_recommendations"] = [
            recommendations_by_id[ref]
            for ref in item.get("recommendation_refs", [])
            if ref in recommendations_by_id
        ]

        if not item.get("summary"):
            item["summary"] = build_fallback_summary(item)

        expanded.append(item)

    return expanded


def build_fallback_summary(finding: Dict[str, Any]) -> str:
    """Generate a deterministic fallback summary when one is missing."""
    title = finding.get("title", "Untitled finding")
    severity = finding.get("severity", "Informational")
    return f"{title} is classified as {severity} and requires review."
