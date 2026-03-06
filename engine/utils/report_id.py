
"""Report ID generator utilities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional


PREFIX_MAP = {
    "risk_assessment": "RISK",
    "osint_brief": "OSINT",
    "pentest": "PENTEST",
    "incident_response": "IR",
    "default": "RPT",
}


def build_report_id(report_type: str, sequence: int, year: Optional[int] = None) -> str:
    resolved_year = year or datetime.utcnow().year
    prefix = PREFIX_MAP.get(report_type, PREFIX_MAP["default"])
    return f"{prefix}-{resolved_year}-{sequence:03d}"
