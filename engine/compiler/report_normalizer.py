
"""Report normalization rules for Metis Report Engine."""

from __future__ import annotations

from typing import Any, Dict, List


SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Informational"]
SEVERITY_MAP = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "moderate": "Medium",
    "low": "Low",
    "info": "Informational",
    "informational": "Informational",
}


def normalize_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a partially structured report into predictable canonical form."""
    report.setdefault("report", {})
    report.setdefault("executive_summary", {})
    report.setdefault("findings", [])
    report.setdefault("evidence", [])
    report.setdefault("recommendations", [])
    report.setdefault("metrics", {})
    report.setdefault("risk_model", {})
    report.setdefault("visualizations", [])
    report.setdefault("appendices", [])

    report["findings"] = [normalize_finding(item, index=i + 1) for i, item in enumerate(report["findings"])]
    report["recommendations"] = [
        normalize_recommendation(item, index=i + 1)
        for i, item in enumerate(report["recommendations"])
    ]
    report["evidence"] = [normalize_evidence(item, index=i + 1) for i, item in enumerate(report["evidence"])]

    report["findings"].sort(key=lambda x: (severity_rank(x.get("severity")), x.get("id", "")))
    report["recommendations"].sort(key=lambda x: (severity_rank(x.get("priority")), x.get("id", "")))

    report["metrics"] = normalize_metrics(report["metrics"], report["findings"])
    return report


def normalize_finding(finding: Dict[str, Any], index: int) -> Dict[str, Any]:
    finding = dict(finding)
    finding.setdefault("id", f"F-{index:03d}")
    finding.setdefault("title", f"Finding {index}")
    finding["severity"] = normalize_severity(finding.get("severity", "Informational"))
    finding["likelihood"] = coerce_int(finding.get("likelihood"), default=None)
    finding["impact"] = coerce_int(finding.get("impact"), default=None)
    finding.setdefault("summary", "")
    finding.setdefault("evidence_refs", [])
    finding.setdefault("recommendation_refs", [])
    return finding


def normalize_recommendation(rec: Dict[str, Any], index: int) -> Dict[str, Any]:
    rec = dict(rec)
    rec.setdefault("id", f"REC-{index:03d}")
    rec.setdefault("title", f"Recommendation {index}")
    rec["priority"] = normalize_severity(rec.get("priority", "Medium"))
    rec.setdefault("summary", "")
    return rec


def normalize_evidence(evidence: Dict[str, Any], index: int) -> Dict[str, Any]:
    evidence = dict(evidence)
    evidence.setdefault("id", f"E-{index:03d}")
    evidence.setdefault("title", f"Evidence {index}")
    evidence.setdefault("type", "document")
    return evidence


def normalize_metrics(metrics: Dict[str, Any], findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    metrics = dict(metrics or {})
    if "risk_distribution" not in metrics:
        distribution = {key.lower(): 0 for key in SEVERITY_ORDER}
        for finding in findings:
            sev = finding.get("severity", "Informational").lower()
            distribution[sev] = distribution.get(sev, 0) + 1
        metrics["risk_distribution"] = distribution
    return metrics


def normalize_severity(value: Any) -> str:
    if value is None:
        return "Informational"
    normalized = SEVERITY_MAP.get(str(value).strip().lower())
    return normalized if normalized else str(value).strip().title()


def severity_rank(value: Any) -> int:
    normalized = normalize_severity(value)
    try:
        return SEVERITY_ORDER.index(normalized)
    except ValueError:
        return len(SEVERITY_ORDER)


def coerce_int(value: Any, default: Any = None) -> Any:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
