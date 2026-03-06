from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_report_json(path: str | Path) -> Dict[str, Any]:
    report_path = Path(path)
    if not report_path.exists():
        raise FileNotFoundError(f"Report JSON not found: {report_path}")
    with report_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
