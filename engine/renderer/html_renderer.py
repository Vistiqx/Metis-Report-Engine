from __future__ import annotations

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path


def render_report_html(payload: dict) -> str:
    template_root = Path(__file__).resolve().parents[2] / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_root)),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("report_template.html")
    return template.render(**payload)
