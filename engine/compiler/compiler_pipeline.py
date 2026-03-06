
"""Compiler pipeline orchestration for Metis Report Engine.

This module coordinates the end-to-end transformation of DSL or partial
report input into canonical report JSON ready for scoring, visualization,
preview rendering, and PDF generation.
"""

from __future__ import annotations

from typing import Any, Dict

from engine.compiler.dsl_compiler import compile_dsl_text
from engine.compiler.report_normalizer import normalize_report
from engine.compiler.finding_expander import expand_findings
from engine.compiler.visualization_resolver import resolve_visualizations


class CompilerPipelineError(Exception):
    """Raised when the compiler pipeline fails."""


def compile_report(
    *,
    dsl_text: str | None = None,
    report_json: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Compile a report into canonical JSON.

    Supported modes:
    - DSL input -> canonical report JSON
    - partial JSON input -> normalized canonical report JSON
    """
    if dsl_text and report_json:
        raise CompilerPipelineError("Provide either dsl_text or report_json, not both.")

    if dsl_text:
        compiled = compile_dsl_text(dsl_text)
    elif report_json:
        compiled = dict(report_json)
        compiled = normalize_report(compiled)
        compiled["findings"] = expand_findings(
            compiled.get("findings", []),
            evidence=compiled.get("evidence", []),
            recommendations=compiled.get("recommendations", []),
        )
        if not compiled.get("visualizations"):
            compiled["visualizations"] = resolve_visualizations(compiled)
    else:
        raise CompilerPipelineError("No report input was provided.")

    return compiled
