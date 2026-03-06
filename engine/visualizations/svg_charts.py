from __future__ import annotations


def severity_distribution_svg(data: dict) -> str:
    critical = int(data.get("critical", 0))
    high = int(data.get("high", 0))
    medium = int(data.get("medium", 0))
    low = int(data.get("low", 0))
    max_value = max(critical, high, medium, low, 1)

    def bar(x: int, value: int, label: str) -> str:
        height = int((value / max_value) * 120)
        y = 140 - height
        return f'<g><rect x="{x}" y="{y}" width="40" height="{height}" rx="6"></rect><text x="{x+20}" y="160" text-anchor="middle">{label}</text><text x="{x+20}" y="{y-6}" text-anchor="middle">{value}</text></g>'

    return (
        '<svg viewBox="0 0 260 180" xmlns="http://www.w3.org/2000/svg">'
        '<style>text{font-family:Inter,Arial,sans-serif;font-size:12px;fill:#121212} rect{fill:#8A6FD6}</style>'
        f'{bar(20, critical, "C")}{bar(80, high, "H")}{bar(140, medium, "M")}{bar(200, low, "L")}'
        '</svg>'
    )
