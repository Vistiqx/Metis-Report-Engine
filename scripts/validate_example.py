from engine.parser.report_loader import load_report_json
from engine.parser.schema_validator import validate_report_payload

payload = load_report_json("examples/example_report.json")
validate_report_payload(payload)
print("Example report is valid.")
