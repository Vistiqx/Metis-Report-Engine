# Master Prompt — Build Metis Report Engine (Optimized for Kimi K2.5)

You are building a standalone application called **Metis Report Engine**.

Your job is to autonomously build the full application in the repository using the provided schemas, docs, examples, theme files, and architecture notes.

## High-level mission

Build an AI-first report generation application that:
- accepts structured report JSON as the source of truth
- validates against JSON schemas
- previews findings, evidence, recommendations, and visualizations
- renders branded executive-grade PDF reports
- is easy to port into the future Metis platform

## Non-negotiable architectural rules

1. **Structured JSON is the canonical data model.**
   - Do not make Markdown the source of truth.
   - Markdown may later be used as a source input, but the renderer must depend on validated JSON report objects.

2. **Separate data, narrative, presentation, and output.**
   - Data = report schema and objects
   - Narrative = summary/explanation text fields in the data
   - Presentation = HTML/CSS/SVG report layout
   - Output = PDF export

3. **Charts must be deterministic.**
   - Use SVG generation from structured data.
   - Do not use AI-generated charts as image blobs.
   - Prefer reusable chart components.

4. **The application must be portable into Metis later.**
   - Keep report schema, theme, chart, and UI logic modular.
   - Use packages or logical boundaries matching the repo layout.

5. **The UI should follow the Metis design language.**
   - Mission-control / operator-console feel
   - Purple gradient palette and typography from theme files
   - Clean professional executive preview for report output

## Primary deliverables

Build:
- web UI
- backend/API
- schema validator
- report preview flow
- deterministic visualization layer
- PDF export pipeline
- example report load flow

## Preferred implementation stack

- Frontend: Next.js + TypeScript + Tailwind
- Backend: FastAPI
- PDF: HTML/CSS/SVG + Playwright
- Validation: JSON Schema

You may adapt details only if necessary, but preserve the architecture and portability goals.

## Required product capabilities

### Report input
- Load structured report JSON from file
- Show validation results
- Show metadata
- Show findings, evidence, recommendations
- Show section list and visualization list

### Report preview
- Cover page preview
- Executive summary preview
- KPI cards
- Risk matrix
- Severity distribution
- Findings table/cards
- Recommendations section
- Appendix / evidence references

### Export
- Generate branded PDF
- Save or return canonical JSON with rendered artifact metadata

## Required engineering standards

- TypeScript types should align to JSON schemas
- Modular component boundaries
- Deterministic rendering
- Strong error handling
- Clear README updates as needed
- Avoid placeholder-only implementation where a working slice can be built

## Build order

1. Read all docs and schemas in this repo.
2. Implement schema loading and validation.
3. Implement the core report data types from schema.
4. Implement the backend report preview and export flow.
5. Implement the frontend pages and layout.
6. Implement deterministic SVG chart components.
7. Implement PDF rendering.
8. Wire up the example report JSON to prove end-to-end flow.
9. Add tests for schema validation and export smoke flow.

## UI expectations

Use a layout with:
- left sidebar navigation
- top header / workspace title
- main preview area
- optional right-side inspector for validation / export options

Navigation should include:
- Dashboard
- Reports
- Templates
- Themes
- Visualizations
- Validation
- Exports
- Settings

## Rendering expectations

PDF output must support:
- executive cover page
- table of contents placeholder or generated TOC
- confidentiality/classification treatment
- section numbering
- repeatable headers/footers
- printable executive-quality visual hierarchy

## Constraints

- Do not redesign the project into a generic CMS.
- Do not use Markdown as the primary report model.
- Do not bury calculations inside the presentation layer.
- Do not create one-off hardcoded views that cannot generalize.

## Use the provided files

You must use:
- `schemas/`
- `docs/`
- `theme/`
- `examples/reports/`
- `prompts/`

If an example is incomplete, infer responsibly and extend with clean patterns.

## Done means

The repo contains a working first slice where:
- the example report loads
- validation runs
- preview renders
- at least several deterministic visuals render
- PDF export works end-to-end

## Final instruction

Build the strongest practical v1 possible while preserving a clean migration path into Metis later.
