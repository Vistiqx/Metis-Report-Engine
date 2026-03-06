from __future__ import annotations

from collections import Counter
from typing import Any, Dict


def summarize_risk_distribution(payload: Dict[str, Any]) -> Dict[str, int]:
    findings = payload.get("findings", [])
    counter = Counter()
    for finding in findings:
        severity = str(finding.get("severity", "Unknown")).strip().lower()
        counter[severity] += 1
    return {
        "critical": counter.get("critical", 0),
        "high": counter.get("high", 0),
        "medium": counter.get("medium", 0),
        "low": counter.get("low", 0)
    }
