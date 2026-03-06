# Provenance Tracking

## Purpose
Track transformation history from input to rendered report.

## Recommended Stages
- original input receipt
- DSL parse
- canonical compilation
- normalization
- validation
- scoring
- visualization generation
- HTML render
- PDF render

## Recommended Metadata
- input type
- source file or request ID
- schema version
- compiler version
- template ID
- theme profile
- timestamps per stage
- validation status
- error status if failed

## Benefit
Supports auditability, debugging, enterprise delivery, and future Metis observability.
