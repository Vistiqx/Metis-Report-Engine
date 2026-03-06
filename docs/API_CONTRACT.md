# API Contract

## Purpose
Define the preferred service/API payloads for the engine and future Metis integration.

## Endpoints

### POST `/validate-dsl`
Validate DSL input without compiling to final PDF.

Request:
```json
{ "dsl": "..." }
```

Response:
```json
{ "valid": true, "errors": [] }
```

### POST `/compile-dsl`
Compile DSL to canonical JSON.

Request:
```json
{ "dsl": "...", "report_type": "risk_assessment" }
```

Response:
```json
{ "report_json": {} }
```

### POST `/validate-report-json`
Validate canonical report JSON.

### POST `/render-html`
Render HTML preview from canonical JSON.

### POST `/render-pdf`
Render PDF from canonical JSON.

### POST `/render-manifest`
Produce render manifest metadata.

## Rules
- canonical JSON is the only render input
- responses must use structured error model on failure
- report type config and theme profile should be explicit inputs where relevant
