# Report Quality Gates

## Purpose
Define minimum quality thresholds before a report may render or publish.

## Required Gates
1. canonical schema validation passes
2. required sections exist for the selected report type
3. all referenced evidence and recommendations resolve
4. severity values are normalized
5. all visualizations have valid data sources
6. executive summary exists where required
7. findings count is at least one unless report type explicitly allows zero-finding outputs

## Optional Gates
- minimum recommendation coverage
- confidence score presence
- appendix completeness
- legal citation presence for relevant report types

## Behavior
Quality gate failures should block PDF generation unless an explicit override policy exists.
