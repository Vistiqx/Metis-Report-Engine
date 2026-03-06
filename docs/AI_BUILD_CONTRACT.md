# AI Build Contract --- Metis Report Engine

## Purpose

This document defines the **non‑negotiable architectural rules** the AI
builder must follow when implementing the Metis Report Engine.

The goal is to ensure the engine remains: - deterministic -
schema‑driven - portable into the Metis platform - compatible with
future intelligence reporting workflows

------------------------------------------------------------------------

# Core Principles

1.  **Canonical Data Model**

    -   The canonical report structure is defined by:
        `schema/metis_report.schema.json`
    -   All reports must validate against this schema.

2.  **DSL as Authoring Layer**

    -   The DSL schema: `schema/metis_report_dsl.schema.json`
    -   DSL must compile into canonical JSON before rendering.

3.  **Rendering Pipeline** The report generation pipeline must follow
    this order:

    Input\
    → DSL or JSON\
    → Schema Validation\
    → Normalization / Compilation\
    → Risk Scoring\
    → Visualization Generation\
    → HTML Rendering\
    → PDF Generation

4.  **Renderer Rules**

    -   The renderer must **only consume canonical JSON**.
    -   Renderer must never parse DSL directly.

5.  **Visualization Requirements** Charts and matrices must be
    deterministic and data driven.

    Examples:

    -   risk matrix
    -   severity distribution
    -   KPI cards
    -   timelines

    Rules:

    -   No invented chart values
    -   No charts derived from unvalidated text

6.  **Theme System** Styling must be driven from theme tokens:

    -   `theme/colors.json`
    -   `theme/typography.json`
    -   `theme/client_profiles/`

    No hardcoded colors or fonts.

7.  **Metis Portability** The engine must remain portable to Metis.

    Therefore:

    -   parser
    -   scoring
    -   visualization
    -   renderer

    must remain modular and independent.

8.  **Structured Intelligence Objects** Reports must be composed from
    structured objects:

    -   findings
    -   evidence
    -   recommendations
    -   metrics
    -   visualizations
    -   risk models

9.  **Schema Governance**

    -   Schema changes require versioning
    -   Example reports must remain valid after schema updates

10. **Test Fixtures** The `examples/` directory contains validation
    fixtures and must not be modified by the renderer.

------------------------------------------------------------------------

# Anti‑Patterns To Avoid

The AI builder must NOT:

-   Render directly from Markdown
-   Mix DSL parsing into renderer templates
-   Generate charts from prose
-   Create separate incompatible schemas per report type
-   Hardcode styling outside theme tokens

------------------------------------------------------------------------

# Expected Architecture

Metis Report Engine should remain organized as:

schema/ engine/ templates/ theme/ examples/ prompts/ docs/

with modular components for parsing, scoring, visualization, and
rendering.
