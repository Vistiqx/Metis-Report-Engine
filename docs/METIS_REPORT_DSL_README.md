# Metis Report DSL Kit

This kit defines a human/AI-friendly Domain Specific Language (DSL) for authoring reports that compile into the canonical Metis Report Engine JSON schema.

## Purpose
- easier for AI to generate reliably than raw JSON
- easier for humans to review than nested JSON
- deterministic to parse into canonical report objects
- portable into Metis later

## Core flow
DSL -> parser -> canonical JSON -> renderer -> PDF

## Included
- `docs/METIS_REPORT_DSL_SPEC.md`
- `docs/DSL_TO_SCHEMA_MAPPING.md`
- `docs/IMPLEMENTATION_NOTES.md`
- `schemas/metis_report_dsl.schema.json`
- `examples/risk_assessment.dsl.md`
- `examples/osint_brief.dsl.md`
- `prompts/KIMI_DSL_AUTHORING_PROMPT.md`
