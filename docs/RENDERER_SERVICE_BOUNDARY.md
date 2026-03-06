# Renderer Service Boundary

## Purpose
Define the renderer as a separable boundary even if it is initially implemented inside the same repository.

## Goal
The renderer should be portable into Metis as a standalone service or internal subsystem without requiring parser, scoring, or normalization logic to be embedded in the UI layer.

## Boundary Definition

### Upstream
The renderer accepts only:
- canonical validated report JSON
- theme profile selection
- render options
- template / report type selection

### Downstream
The renderer produces:
- HTML preview
- PDF artifact
- render manifest
- structured render errors

## Non-Goals
The renderer must not:
- parse Markdown
- parse DSL directly
- normalize report content
- calculate risk scores
- infer missing fields

## Suggested Internal API
- `render_html(report_json, template_id, theme_profile, options)`
- `render_pdf(report_json, template_id, theme_profile, options)`
- `render_manifest(report_json, template_id, theme_profile, options)`

## Suggested Service API
- `POST /render/html`
- `POST /render/pdf`
- `POST /render/manifest`

## Porting Benefit
When ported to Metis:
- report generation can be queued
- preview rendering can be isolated
- PDF rendering can scale independently
- failures are contained to a render subsystem
