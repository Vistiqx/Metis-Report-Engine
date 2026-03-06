# AI Output Contract --- Metis Report Engine

## Purpose

This document defines the **output structure AI systems must follow**
when generating structured intelligence reports.

All generated reports must conform to the canonical schema:

`schema/metis_report.schema.json`

------------------------------------------------------------------------

# Canonical Report Structure

A valid report must contain the following top‑level sections:

report executive_summary findings recommendations metrics visualizations

Optional sections may include:

evidence appendices engagement risk_model

------------------------------------------------------------------------

# Example Minimal Report JSON

``` json
{
  "report": {
    "id": "RPT-001",
    "title": "Example Risk Assessment",
    "classification": "Confidential"
  },

  "executive_summary": {
    "overall_risk_rating": "High"
  },

  "findings": [
    {
      "id": "F-001",
      "title": "Example Finding",
      "severity": "High",
      "summary": "Example issue description."
    }
  ],

  "recommendations": [
    {
      "id": "REC-001",
      "title": "Example Recommendation",
      "priority": "High"
    }
  ]
}
```

------------------------------------------------------------------------

# Rules for AI Generated Reports

1.  **IDs must be stable**

    -   Findings, evidence, and recommendations must have unique
        identifiers.

2.  **Relationships must be explicit**

    -   Findings may reference evidence and recommendations by ID.

3.  **Severity must be normalized** Allowed values:

    -   Critical
    -   High
    -   Medium
    -   Low
    -   Informational

4.  **Metrics must be numeric** All charts derive from numeric metrics.

5.  **Narrative must remain separate from structure** Descriptive text
    must not replace structured fields.

------------------------------------------------------------------------

# DSL Compilation

If reports are authored using the Metis DSL:

DSL → Compiler → Canonical JSON → Renderer

The DSL must never bypass the canonical schema.

------------------------------------------------------------------------

# Validation

Before rendering, the report must:

1.  Pass JSON schema validation
2.  Contain required report metadata
3.  Contain at least one finding

------------------------------------------------------------------------

# Rendering Guarantee

If a report validates successfully against the canonical schema, the
renderer must be able to generate:

-   HTML preview
-   PDF report
