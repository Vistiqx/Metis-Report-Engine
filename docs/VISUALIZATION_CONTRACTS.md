# Visualization Contracts

## Purpose
Define the deterministic, reusable visual components the renderer may produce.

## Supported Visualization Types

### 1. Severity Distribution
Input:
- `metrics.risk_distribution`

Output:
- deterministic chart
- ordered severities: Critical, High, Medium, Low, Informational

### 2. Risk Matrix
Input:
- `risk_model.matrix`

Output:
- deterministic impact x likelihood matrix
- no AI-inferred placement

### 3. KPI Summary Cards
Input:
- `executive_summary`
- `metrics`

Output:
- numeric and normalized values only

### 4. Timeline
Input:
- timeline or recommendation scheduling data
- incident timeline data where applicable

Output:
- ordered chronological visualization

### 5. Comparison Table
Input:
- structured comparison rows only

Output:
- deterministic table rendering

## Rules
- visualizations must be fully derivable from structured data
- visualization generation must fail fast on invalid source references
- no chart values may be invented from prose
- the same data must always produce the same visual structure

## Renderer Contract
Each visualization definition should include:
- `id`
- `type`
- `title`
- `data_source`
- `style_variant`
- `options`
