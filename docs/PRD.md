# Metis Report Engine PRD

## Objective

Create a standalone application that transforms structured security and intelligence report JSON into polished, branded PDF reports.

## Current Goal

- Deliver client-ready report generation now
- Preserve architecture for future migration into Metis

## Non-Negotiables

- JSON schemas define the source-of-truth contracts
- Findings, Evidence, Recommendations, Metrics, Risk Models, and Visualizations are first-class objects
- Rendering must be modular and reusable
- Brand theme tokens must be configurable
- Domain-specific extensions must inherit from the shared core models

## Report Types Initially Targeted

- Risk Assessment
- Security Assessment
- Executive Intelligence Brief

## Future Metis Portability Requirements

- API boundaries remain clean
- Models remain independent from view templates
- Theme system remains tokenized
- Visualizations remain reusable components
- Contracts remain stable across app and platform contexts
