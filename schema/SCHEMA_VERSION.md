# Schema Versioning

## Current Canonical Schema Version
- `metis_report.schema.json`: `v1.0.0`
- `metis_report_dsl.schema.json`: `v1.0.0`

## Versioning Rules
1. Patch version
   - non-breaking clarifications
   - documentation-only updates
   - optional field additions that do not affect existing valid inputs

2. Minor version
   - additive structured capabilities
   - new optional sections
   - new supported visualization contracts

3. Major version
   - breaking field changes
   - renamed required fields
   - removed sections
   - changed validation semantics

## Required Change Process
- update schema version
- update example fixtures
- update migration notes
- update API contract if payloads change
- update report manifest format if impacted

## Compatibility Target
The engine should preserve backward compatibility for all example fixtures within the same major version.
