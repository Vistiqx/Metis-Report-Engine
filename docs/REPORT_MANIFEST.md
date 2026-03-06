# Report Manifest

## Purpose
Define metadata emitted for each rendered report.

## Suggested Shape
```json
{
  "report_id": "RPT-001",
  "report_type": "risk_assessment",
  "schema_version": "v1.0.0",
  "dsl_schema_version": "v1.0.0",
  "template_id": "default_risk_assessment",
  "theme_profile": "consulting_light",
  "rendered_at": "2026-03-06T00:00:00Z",
  "validation_status": "passed",
  "visualizations": ["severity_distribution", "risk_matrix"],
  "output_files": {
    "html": "preview.html",
    "pdf": "report.pdf"
  }
}
```

## Benefits
- auditability
- reproducibility
- supportability
- easier Metis ingestion later
