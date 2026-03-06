
"""Simple deterministic chart cache for Metis Report Engine."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional


class ChartCache:
    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def make_key(self, visualization_type: str, payload: Dict[str, Any]) -> str:
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return f"{visualization_type}:{digest}"

    def get(self, visualization_type: str, payload: Dict[str, Any]) -> Optional[str]:
        return self._cache.get(self.make_key(visualization_type, payload))

    def set(self, visualization_type: str, payload: Dict[str, Any], rendered: str) -> None:
        self._cache[self.make_key(visualization_type, payload)] = rendered

    def clear(self) -> None:
        self._cache.clear()
