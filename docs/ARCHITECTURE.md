# Architecture

## Pipeline

Inputs / Instructions / Evidence
-> AI structured output
-> Schema validation
-> Deterministic scoring and metric derivation
-> Visualization declaration + generation
-> HTML render
-> PDF export

## Layers

1. Contracts
2. Parser / Validation
3. Scoring
4. Visualization components
5. Templating
6. PDF export

## Metis Port Path

This app should later become a Metis subsystem by:
- moving schemas into shared Metis contracts
- exposing the rendering pipeline as a service
- swapping file-based input for Metis object-store / API inputs
- reusing the same theme tokens and visualization library
