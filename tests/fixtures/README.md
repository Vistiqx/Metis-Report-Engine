# Golden Test Fixtures

## Purpose
These fixtures support deterministic regression testing.

## Layout
- `input/` raw or compiled inputs used by tests
- `expected_json/` canonical normalized JSON outputs
- `expected_html/` expected HTML snapshot fragments
- `expected_pdf_checks/` metadata or assertions for PDF validation

## Rule
AI builders must treat these as test fixtures, not as runtime templates.
