from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator, RefResolver

SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schema"
MASTER_SCHEMA = SCHEMA_ROOT / "metis_report.schema.json"


def validate_report_payload(payload: dict) -> None:
    with MASTER_SCHEMA.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)

    resolver = RefResolver(base_uri=MASTER_SCHEMA.as_uri(), referrer=schema)
    validator = Draft202012Validator(schema, resolver=resolver)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    if errors:
        joined = "; ".join(error.message for error in errors)
        raise ValueError(f"Schema validation failed: {joined}")
