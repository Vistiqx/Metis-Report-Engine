# Component Registry

## Purpose
Define the reusable render components available to report assemblies.

## Components
- `CoverPage`
- `ExecutiveSummary`
- `MetricCards`
- `SeverityDistribution`
- `RiskMatrix`
- `Timeline`
- `FindingsOverview`
- `DetailedFindings`
- `RecommendationsTable`
- `ComparisonTable`
- `AppendixBlock`

## Registry Rules
- components must consume structured data only
- components should be configurable by theme tokens
- components should be reusable across report types
- component output should be deterministic for equivalent inputs
