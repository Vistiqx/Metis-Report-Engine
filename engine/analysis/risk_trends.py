"""Risk trend analysis for Metis Report Engine.

This module provides deterministic analysis of risk trends over time,
identifying changes in risk exposure and tracking remediation progress.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


def build_risk_trend_series(periods: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a deterministic risk trend structure from historical period inputs.

    Expected input example:
    [
      {"label": "2025-01", "critical": 2, "high": 5, "medium": 7, "low": 3},
      ...
    ]
    """
    series = {
        "labels": [],
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
        "informational": [],
    }

    for period in periods:
        series["labels"].append(period.get("label", "unknown"))
        series["critical"].append(int(period.get("critical", 0)))
        series["high"].append(int(period.get("high", 0)))
        series["medium"].append(int(period.get("medium", 0)))
        series["low"].append(int(period.get("low", 0)))
        series["informational"].append(int(period.get("informational", 0)))

    return series


def analyze_risk_trends(
    current_report: Dict[str, Any],
    previous_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Analyze risk trends between current and previous reports.
    
    Args:
        current_report: The current report data
        previous_report: Optional previous report for comparison
        
    Returns:
        Dictionary containing trend analysis results
    """
    trends = {
        "overall_trend": "stable",
        "severity_changes": {},
        "new_findings": [],
        "resolved_findings": [],
        "risk_score_delta": 0,
        "trend_summary": "",
    }
    
    if not previous_report:
        # No baseline, just analyze current state
        trends["trend_summary"] = _generate_baseline_summary(current_report)
        return trends
    
    # Compare current vs previous
    current_findings = {f["id"]: f for f in current_report.get("findings", [])}
    previous_findings = {f["id"]: f for f in previous_report.get("findings", [])}
    
    # Find new findings
    new_ids = set(current_findings.keys()) - set(previous_findings.keys())
    trends["new_findings"] = list(new_ids)
    
    # Find resolved findings
    resolved_ids = set(previous_findings.keys()) - set(current_findings.keys())
    trends["resolved_findings"] = list(resolved_ids)
    
    # Analyze severity changes for common findings
    severity_changes = {}
    for fid in set(current_findings.keys()) & set(previous_findings.keys()):
        current_sev = current_findings[fid].get("severity", "Informational")
        previous_sev = previous_findings[fid].get("severity", "Informational")
        if current_sev != previous_sev:
            severity_changes[fid] = {
                "from": previous_sev,
                "to": current_sev,
            }
    trends["severity_changes"] = severity_changes
    
    # Calculate overall trend
    trends["overall_trend"] = _calculate_overall_trend(
        trends["new_findings"],
        trends["resolved_findings"],
        severity_changes,
    )
    
    # Calculate risk score delta
    trends["risk_score_delta"] = _calculate_risk_delta(
        current_findings,
        previous_findings,
    )
    
    trends["trend_summary"] = _generate_trend_summary(trends)
    
    return trends


def _calculate_overall_trend(
    new_findings: List[str],
    resolved_findings: List[str],
    severity_changes: Dict[str, Dict[str, str]],
) -> str:
    """Calculate the overall risk trend direction."""
    severity_order = ["Informational", "Low", "Medium", "High", "Critical"]
    
    # Count improvements vs degradations
    improvements = 0
    degradations = 0
    
    for change in severity_changes.values():
        from_idx = severity_order.index(change["from"])
        to_idx = severity_order.index(change["to"])
        if to_idx < from_idx:
            degradations += 1
        elif to_idx > from_idx:
            improvements += 1
    
    # Overall assessment
    if len(new_findings) > len(resolved_findings):
        return "increasing"
    elif len(resolved_findings) > len(new_findings):
        return "decreasing"
    elif degradations > improvements:
        return "increasing"
    elif improvements > degradations:
        return "decreasing"
    else:
        return "stable"


def _calculate_risk_delta(
    current_findings: Dict[str, Any],
    previous_findings: Dict[str, Any],
) -> int:
    """Calculate the change in total risk score."""
    def get_score(finding):
        risk = finding.get("risk", {})
        return risk.get("score", 0)
    
    current_total = sum(get_score(f) for f in current_findings.values())
    previous_total = sum(get_score(f) for f in previous_findings.values())
    
    return current_total - previous_total


def _generate_baseline_summary(report: Dict[str, Any]) -> str:
    """Generate a summary when there's no baseline report."""
    findings = report.get("findings", [])
    severity_counts = {}
    for f in findings:
        sev = f.get("severity", "Informational")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    parts = []
    for sev in ["Critical", "High", "Medium", "Low", "Informational"]:
        if sev in severity_counts:
            parts.append(f"{severity_counts[sev]} {sev.lower()}")
    
    if parts:
        return f"Initial assessment: {', '.join(parts)}"
    return "Initial assessment: no findings"


def _generate_trend_summary(trends: Dict[str, Any]) -> str:
    """Generate a human-readable trend summary."""
    parts = []
    
    if trends["new_findings"]:
        parts.append(f"{len(trends['new_findings'])} new finding(s)")
    
    if trends["resolved_findings"]:
        parts.append(f"{len(trends['resolved_findings'])} resolved finding(s)")
    
    if trends["severity_changes"]:
        parts.append(f"{len(trends['severity_changes'])} severity change(s)")
    
    if trends["risk_score_delta"] > 0:
        parts.append(f"risk score increased by {trends['risk_score_delta']}")
    elif trends["risk_score_delta"] < 0:
        parts.append(f"risk score decreased by {abs(trends['risk_score_delta'])}")
    else:
        parts.append("risk score unchanged")
    
    trend = trends["overall_trend"]
    if trend == "increasing":
        parts.append("overall risk is increasing")
    elif trend == "decreasing":
        parts.append("overall risk is decreasing")
    else:
        parts.append("risk is stable")
    
    return "; ".join(parts)


def calculate_risk_velocity(
    reports: List[Dict[str, Any]],
    date_field: str = "date_created",
) -> Dict[str, Any]:
    """Calculate risk velocity across multiple reports.
    
    Args:
        reports: List of reports in chronological order
        date_field: Field name for report date
        
    Returns:
        Velocity metrics
    """
    if len(reports) < 2:
        return {
            "velocity": 0,
            "trend": "insufficient_data",
            "message": "Need at least 2 reports to calculate velocity",
        }
    
    # Extract risk scores
    scores = []
    dates = []
    
    for report in reports:
        findings = report.get("findings", [])
        score = sum(
            f.get("risk", {}).get("score", 0)
            for f in findings
        )
        scores.append(score)
        
        # Parse date
        date_str = report.get("report", {}).get(date_field)
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                dates.append(date)
            except ValueError:
                dates.append(None)
        else:
            dates.append(None)
    
    # Calculate velocity (change per time unit)
    total_change = scores[-1] - scores[0]
    
    # Determine trend
    if total_change > 0:
        trend = "increasing"
    elif total_change < 0:
        trend = "decreasing"
    else:
        trend = "stable"
    
    return {
        "velocity": total_change / max(1, len(scores) - 1),
        "total_change": total_change,
        "trend": trend,
        "scores": scores,
        "message": f"Risk velocity: {total_change / max(1, len(scores) - 1):.2f} per report",
    }
