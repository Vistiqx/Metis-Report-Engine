
"""Table of contents generator for report sections."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def build_toc(sections: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    toc = []
    for index, section in enumerate(sections, start=1):
        toc.append({
            "index": index,
            "title": section.get("title", f"Section {index}"),
            "anchor": section.get("anchor", f"section-{index}"),
            "page_hint": section.get("page_hint"),
        })
    return toc
