# Executive OSINT Brief

```report
id: RPT-2026-OSINT-001
report_type: osint_brief
title: Executive OSINT Brief
client: Internal
classification: Internal
version: 1.0
```

```executive_summary
overall_risk_rating: Medium
summary: |
  Publicly accessible information increases targeting exposure.
```

```evidence
id: E-OS-001
title: Public employee directory listing
type: web_source
subtype: public_listing
source_name: Corporate website
capture_url: https://example.org/team
trust_level: Medium
summary: |
  Public employee identities and role data were accessible.
```

```finding
id: F-OS-001
title: Excessive Public Staff Exposure
domain: osint
category: Exposure
severity: Medium
likelihood: 3
impact: 3
summary: |
  Public staff information can increase targeting and social engineering risk.
evidence_refs:
  - E-OS-001
```
