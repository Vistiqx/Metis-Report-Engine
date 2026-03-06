
"""Risk matrix generator for Metis Report Engine."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable


def render_risk_matrix_svg(data: Dict[str, Any]) -> str:
    """Render a simple deterministic 5x5 risk matrix as SVG.

    Expected input:
    {
        "findings": [{"likelihood": 4, "impact": 5, "title": "..."}, ...]
    }
    """
    findings = data.get("findings", [])
    counts = defaultdict(int)
    for finding in findings:
        likelihood = _bounded_int(finding.get("likelihood"))
        impact = _bounded_int(finding.get("impact"))
        if likelihood and impact:
            counts[(likelihood, impact)] += 1

    cell_size = 90
    padding = 60
    width = padding + (cell_size * 5) + 20
    height = padding + (cell_size * 5) + 40

    def cell_color(score: int) -> str:
        if score >= 20:
            return "#AC8FFE"
        if score >= 12:
            return "#8A6FD6"
        if score >= 6:
            return "#CFC4F7"
        return "#E8E8F8"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="20" y="24" font-size="18" font-family="Inter, Segoe UI, Arial, sans-serif" fill="#121212">Risk Matrix</text>',
    ]

    for row in range(5):
        impact = 5 - row
        y = padding + row * cell_size
        parts.append(
            f'<text x="20" y="{y + 52}" font-size="14" font-family="Inter, Segoe UI, Arial, sans-serif" fill="#4C3D75">{impact}</text>'
        )
        for col in range(5):
            likelihood = col + 1
            x = padding + col * cell_size
            score = likelihood * impact
            count = counts[(likelihood, impact)]
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'fill="{cell_color(score)}" stroke="#4C3D75" stroke-width="1"/>'
            )
            if count:
                parts.append(
                    f'<text x="{x + cell_size/2}" y="{y + cell_size/2 + 6}" text-anchor="middle" '
                    f'font-size="18" font-family="Inter, Segoe UI, Arial, sans-serif" fill="#121212">{count}</text>'
                )

    for col in range(5):
        likelihood = col + 1
        x = padding + col * cell_size + cell_size / 2
        parts.append(
            f'<text x="{x}" y="{padding + (cell_size*5) + 22}" text-anchor="middle" '
            f'font-size="14" font-family="Inter, Segoe UI, Arial, sans-serif" fill="#4C3D75">{likelihood}</text>'
        )

    parts.append(
        f'<text x="{padding + (cell_size*2.5)}" y="{padding + (cell_size*5) + 38}" text-anchor="middle" '
        f'font-size="14" font-family="Inter, Segoe UI, Arial, sans-serif" fill="#121212">Likelihood</text>'
    )
    parts.append('</svg>')
    return "".join(parts)


def _bounded_int(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    if 1 <= number <= 5:
        return number
    return None
