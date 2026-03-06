# Metis Report DSL Specification v0.1

## Design goals
- predictable for AI generation
- readable in plain text / Markdown
- extensible by report domain
- compilable into canonical JSON objects
- suitable for one-off app now and Metis later

## File format
The DSL is a Markdown-like document with fenced blocks. Each block begins with a type label and YAML payload.

### Allowed top-level blocks
- `report`
- `engagement`
- `executive_summary`
- `metric`
- `finding`
- `evidence`
- `recommendation`
- `visualization`
- `appendix`

## Example syntax

```markdown
# Meta AI Glasses Risk Assessment

```report
id: RPT-2026-001
report_type: risk_assessment
title: Meta AI Glasses Risk Assessment
client: Signal Security
classification: Confidential
version: 1.0
```

```executive_summary
overall_risk_rating: High
summary: |
  The assessed deployment presents material privacy and legal exposure.
```

```metric
id: MET-001
name: risk_distribution
critical: 2
high: 5
medium: 7
low: 3
```

```finding
id: F-001
title: Unauthorized Biometric Capture
domain: risk_assessment
category: Privacy
severity: Critical
likelihood: 4
impact: 5
summary: |
  The workflow allows biometric collection without enforceable consent.
evidence_refs:
  - E-001
recommendation_refs:
  - REC-001
```
```

## Rules
1. Each block must use one of the allowed block types.
2. Each object must have a stable `id`.
3. Relationship references must point to existing IDs.
4. Narrative text should go in `summary`, `description`, `business_impact`, etc.
5. Charts and visuals are declared, not hand-drawn.
6. The compiler converts this DSL into canonical Metis JSON.

## Block definitions

### report
Required:
- `id`
- `report_type`
- `title`

Optional:
- `client`
- `classification`
- `author`
- `version`
- `date_created`
- `date_published`

### engagement
Describes the project context.

### executive_summary
At least one executive summary block is recommended.

### metric
Metrics are structured values used by visuals and summaries.

### finding
Core analysis object.

Recommended fields:
- `id`
- `title`
- `domain`
- `category`
- `severity`
- `likelihood`
- `impact`
- `summary`

### evidence
Supporting proof for a finding.

### recommendation
Action that addresses one or more findings.

### visualization
A declaration telling the render engine what visual to include.

Example:
```markdown
```visualization
id: V-001
type: risk_matrix
data_source: risk_model.matrix
title: Likelihood vs Impact
style_variant: executive
```
```

### appendix
Free-form trailing content.
