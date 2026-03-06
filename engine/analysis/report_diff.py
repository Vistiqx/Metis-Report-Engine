
"""Report diff engine for comparing two canonical reports."""

from __future__ import annotations

from typing import Any, Dict


def diff_reports(old_report: Dict[str, Any], new_report: Dict[str, Any]) -> Dict[str, Any]:
    old_findings = {item.get("id"): item for item in old_report.get("findings", [])}
    new_findings = {item.get("id"): item for item in new_report.get("findings", [])}

    added = [fid for fid in new_findings if fid not in old_findings]
    removed = [fid for fid in old_findings if fid not in new_findings]

    severity_changes = []
    for fid in set(old_findings).intersection(new_findings):
        old_sev = old_findings[fid].get("severity")
        new_sev = new_findings[fid].get("severity")
        if old_sev != new_sev:
            severity_changes.append({
                "id": fid,
                "old_severity": old_sev,
                "new_severity": new_sev,
            })

    return {
        "added_findings": added,
        "removed_findings": removed,
        "severity_changes": severity_changes,
    }
