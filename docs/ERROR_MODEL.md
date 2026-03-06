# Error Model

## Purpose
Define canonical error behavior for parser, validator, compiler, scoring, visualization, and renderer flows.

## Error Envelope
```json
{
  "error": {
    "code": "SCHEMA_VALIDATION_FAILED",
    "message": "Human readable message",
    "stage": "validation",
    "details": [],
    "retryable": false
  }
}
```

## Error Stages
- ingestion
- parsing
- validation
- normalization
- compilation
- scoring
- visualization
- rendering
- pdf_generation

## Common Error Codes
- `DSL_PARSE_FAILED`
- `SCHEMA_VALIDATION_FAILED`
- `MISSING_REQUIRED_SECTION`
- `UNRESOLVED_REFERENCE`
- `RISK_SCORING_FAILED`
- `VISUALIZATION_SOURCE_INVALID`
- `HTML_RENDER_FAILED`
- `PDF_RENDER_FAILED`

## Rules
- errors must be structured
- errors must identify stage
- errors must not leak raw stack traces to end users
- internal logging may preserve diagnostic detail
