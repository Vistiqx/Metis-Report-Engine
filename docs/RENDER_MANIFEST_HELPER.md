
# Render Manifest Helper

## Purpose
This helper creates a structured manifest every time a report is rendered.

## File
- `engine/renderer/render_manifest.py`

## Why this is useful
It improves:
- auditability
- troubleshooting
- reproducibility
- future Metis ingestion
- version tracking for schema, template, and theme profile

## Recommended Integration
Use it at the end of HTML and PDF rendering.

Example flow:
1. canonical JSON validated
2. HTML rendered
3. PDF rendered
4. manifest generated
5. manifest optionally written to disk or returned via API

## Recommended future usage
- store alongside output artifacts
- return from render endpoints
- attach to Metis job records
