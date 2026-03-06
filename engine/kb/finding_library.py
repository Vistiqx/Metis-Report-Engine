
"""Simple finding knowledge base for reusable structured findings."""

from __future__ import annotations

from typing import Any, Dict, Optional


FINDING_LIBRARY: dict[str, Dict[str, Any]] = {
    "missing_mfa": {
        "title": "Missing Multi-Factor Authentication",
        "category": "Identity",
        "severity": "High",
        "summary": "Accounts are not protected by multi-factor authentication.",
    },
    "weak_password_policy": {
        "title": "Weak Password Policy",
        "category": "Authentication",
        "severity": "Medium",
        "summary": "Password policy does not enforce adequate complexity or rotation controls.",
    },
}


def get_finding_template(key: str) -> Optional[Dict[str, Any]]:
    return FINDING_LIBRARY.get(key)


def list_finding_templates() -> list[str]:
    return sorted(FINDING_LIBRARY.keys())
