# Normalization Rules

## Purpose
Define how raw JSON or compiled DSL should be normalized before scoring and rendering.

## Required Normalization

### IDs
- ensure required IDs exist
- generate deterministic IDs only where policy allows
- preserve user-supplied stable IDs when valid

### Severity
Normalize allowed values to:
- Critical
- High
- Medium
- Low
- Informational

### Dates
Normalize dates into ISO formats where applicable.

### References
- resolve `evidence_refs`
- resolve `recommendation_refs`
- fail on unresolved required references

### Missing Optional Fields
- apply documented defaults
- do not fabricate semantically meaningful content

### Ordering
- findings ordered by severity then ID unless report config overrides
- recommendations ordered by priority then timeline unless report config overrides

## Forbidden
- inventing numeric metrics from prose
- silently dropping invalid references
- mutating canonical semantics during render
