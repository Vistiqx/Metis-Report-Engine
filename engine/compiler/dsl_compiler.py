
"""DSL compiler for Metis Report Engine.

Converts the Metis report DSL into canonical report JSON structures.
This module is intentionally conservative and deterministic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List

from .finding_expander import expand_findings
from .report_normalizer import normalize_report
from .visualization_resolver import resolve_visualizations


BLOCK_PATTERN = re.compile(
    r"```(?P<block_type>[a-zA-Z0-9_-]+)\n(?P<body>.*?)```",
    re.DOTALL,
)


@dataclass
class DSLBlock:
    block_type: str
    body: str


class DSLCompilerError(Exception):
    """Raised when DSL compilation fails."""


def compile_dsl_text(dsl_text: str) -> Dict[str, Any]:
    """Compile DSL text into canonical report JSON.

    Expected flow:
    DSL -> parsed blocks -> structured report object -> normalization
    -> finding expansion -> visualization resolution -> canonical JSON
    """
    if not dsl_text or not dsl_text.strip():
        raise DSLCompilerError("DSL input is empty.")

    blocks = parse_dsl_blocks(dsl_text)
    if not blocks:
        raise DSLCompilerError("No DSL blocks were found in the input.")

    report: Dict[str, Any] = {
        "report": {},
        "executive_summary": {},
        "findings": [],
        "evidence": [],
        "recommendations": [],
        "metrics": {},
        "risk_model": {},
        "visualizations": [],
        "appendices": [],
    }

    for block in blocks:
        data = parse_key_value_block(block.body)

        if block.block_type == "report":
            report["report"].update(data)
        elif block.block_type == "executive_summary":
            report["executive_summary"].update(data)
        elif block.block_type == "finding":
            report["findings"].append(data)
        elif block.block_type == "evidence":
            report["evidence"].append(data)
        elif block.block_type == "recommendation":
            report["recommendations"].append(data)
        elif block.block_type == "metric":
            report["metrics"].update(data)
        elif block.block_type == "risk_model":
            report["risk_model"].update(data)
        elif block.block_type == "visualization":
            report["visualizations"].append(data)
        elif block.block_type == "appendix":
            report["appendices"].append(data)
        else:
            # Unknown blocks are ignored intentionally for forward-compatibility.
            continue

    report = normalize_report(report)
    report["findings"] = expand_findings(
        report.get("findings", []),
        evidence=report.get("evidence", []),
        recommendations=report.get("recommendations", []),
    )

    if not report.get("visualizations"):
        report["visualizations"] = resolve_visualizations(report)

    return report


def parse_dsl_blocks(dsl_text: str) -> List[DSLBlock]:
    """Extract fenced DSL blocks from the provided text."""
    blocks: List[DSLBlock] = []
    for match in BLOCK_PATTERN.finditer(dsl_text):
        blocks.append(
            DSLBlock(
                block_type=match.group("block_type").strip(),
                body=match.group("body").strip(),
            )
        )
    return blocks


def parse_key_value_block(body: str) -> Dict[str, Any]:
    """Parse a simple key-value DSL block.

    Supported patterns:
    - key: value
    - multiline block scalars via `|` are preserved
    - simple lists using `- item`
    """
    result: Dict[str, Any] = {}
    lines = body.splitlines()
    idx = 0

    while idx < len(lines):
        raw_line = lines[idx]
        line = raw_line.rstrip()

        if not line.strip():
            idx += 1
            continue

        if ":" not in line:
            idx += 1
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == "|":
            idx += 1
            multi: List[str] = []
            while idx < len(lines):
                next_line = lines[idx]
                if next_line.startswith("  ") or next_line.startswith("\t"):
                    multi.append(next_line.lstrip())
                    idx += 1
                elif not next_line.strip():
                    multi.append("")
                    idx += 1
                else:
                    break
            result[key] = "\n".join(multi).strip()
            continue

        if value == "":
            idx += 1
            items: List[str] = []
            while idx < len(lines):
                next_line = lines[idx].strip()
                if next_line.startswith("- "):
                    items.append(next_line[2:].strip())
                    idx += 1
                elif not next_line:
                    idx += 1
                else:
                    break
            result[key] = items if items else []
            continue

        result[key] = coerce_scalar(value)
        idx += 1

    return result


def coerce_scalar(value: str) -> Any:
    """Coerce scalar values into int/float/bool where safe."""
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
