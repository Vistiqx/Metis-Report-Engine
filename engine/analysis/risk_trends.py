
"""Risk trend analysis helpers."""

from __future__ import annotations

from typing import Any, Dict, List


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
