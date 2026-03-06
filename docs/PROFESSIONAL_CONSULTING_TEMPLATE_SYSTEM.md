
# Professional Consulting Report Template System

## Purpose
This template system gives Metis Report Engine a consulting-grade PDF layout designed for executive-facing security reports.

## Design Direction
The templates use the Vistiqx brand palette:
- Tropical Indigo: `#AC8FFE`
- Amethyst: `#8A6FD6`
- Ultra Violet: `#4C3D75`
- Night: `#121212`
- Lavender: `#E8E8F8`
- Dim Gray: `#6E6E80`

## Typography
The CSS and profile are token-driven and intentionally consume the engine's existing `theme/typography.json`.
This means the visual system is aligned to your company typography configuration without hardcoding a different font identity here.

## Included Files
- `templates/professional_consulting_report.html`
- `templates/components/executive_summary.html`
- `templates/components/findings_table.html`
- `templates/components/recommendations_table.html`
- `templates/styles/professional_consulting.css`
- `theme/client_profiles/vistiqx_consulting.json`

## Recommended Usage
1. Render canonical report JSON with the `vistiqx_consulting` theme profile.
2. Route visualizations through the chart registry.
3. Use this template for:
   - risk assessments
   - executive briefs
   - technical advisory reports
   - client-facing intelligence summaries
