from pathlib import Path
from engine.parser.report_loader import load_report_json
from engine.parser.schema_validator import validate_report_payload
from engine.scoring.risk_calculator import summarize_risk_distribution
from engine.renderer.html_renderer import render_report_html

payload = load_report_json("examples/example_report.json")
validate_report_payload(payload)
payload["derived_metrics"] = summarize_risk_distribution(payload)
html = render_report_html(payload)
output = Path("outputs/example_preview.html")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(html, encoding="utf-8")
print(f"Preview written to {output}")
