# Metis Report Engine

Metis Report Engine is a standalone report-generation application designed to convert structured security and intelligence JSON into branded PDF reports.

This project is intentionally structured so it can be built as a one-off application now and later ported into Metis with minimal architectural change.

## Core Principles

- Structured report JSON is the source of truth
- Rendering is separated from intelligence data models
- Visualizations are deterministic and schema-driven
- Themes are token-based for future client and Metis reuse
- Domain extensions build on a shared core model

## High-Level Flow

1. AI generates canonical report JSON
2. JSON is validated against schemas
3. Metrics and visuals are computed deterministically
4. HTML preview is generated from reusable components
5. PDF is exported from the rendered report

## Initial Stack

- Python
- FastAPI
- Pydantic
- Jinja2
- Playwright
- JSON Schema

## Local Project Path

Place this project at:

`D:\__Projects\Metis-Report-Engine`

## Suggested Startup

```bash
pip install -r requirements.txt
playwright install
uvicorn main:app --reload
```
