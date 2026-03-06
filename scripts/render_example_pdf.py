from pathlib import Path
from engine.parser.report_loader import load_report_json
from engine.parser.schema_validator import validate_report_payload
from engine.scoring.risk_calculator import summarize_risk_distribution
from engine.renderer.html_renderer import render_report_html
from engine.renderer.pdf_renderer import render_pdf_from_html

payload = load_report_json("examples/example_report.json")
validate_report_payload(payload)
payload["derived_metrics"] = summarize_risk_distribution(payload)
html = render_report_html(payload)
output = Path("outputs/example_report.pdf")
output.parent.mkdir(parents=True, exist_ok=True)
render_pdf_from_html(html, output)
print(f"PDF written to {output}")
