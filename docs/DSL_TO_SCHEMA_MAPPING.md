# DSL to Canonical Schema Mapping

## Core principle
The DSL is not the source of truth. The compiled JSON is.

## Mapping examples

### `report` block
Maps to:
- `report.id`
- `report.type`
- `report.title`
- `report.client`
- `report.classification`
- `report.version`

### `executive_summary` block
Maps to:
- `executive_summary.overall_risk_rating`
- `executive_summary.summary`
- `executive_summary.top_risks`
- `executive_summary.key_statistics`

### `finding` block
Maps to a single object in `findings[]`.

Fields:
- `id` -> `findings[].id`
- `title` -> `findings[].title`
- `domain` -> `findings[].domain`
- `category` -> `findings[].category`
- `severity` -> `findings[].severity`
- `likelihood` -> `findings[].risk.likelihood`
- `impact` -> `findings[].risk.impact`
- `summary` -> `findings[].summary`
- `description` -> `findings[].description`
- `business_impact` -> `findings[].business_impact`
- `evidence_refs` -> `findings[].evidence_refs`
- `recommendation_refs` -> `findings[].recommendation_refs`

### `evidence` block
Maps to one object in `evidence[]`.

### `recommendation` block
Maps to one object in `recommendations[]`.

### `metric` block
Maps to `metrics` namespace or metric collection depending on metric type.

### `visualization` block
Maps to `visualizations[]`.
