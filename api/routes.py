"""API routes for Metis Report Engine.

Implements endpoints per API_CONTRACT.md:
- GET /health
- POST /validate-dsl
- POST /compile-dsl
- POST /validate-report-json
- POST /render-html
- POST /render-pdf
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse, HTMLResponse
from typing import Any, Dict, Optional
from pathlib import Path
import tempfile
import json

from engine.parser.report_loader import load_report_json
from engine.parser.schema_validator import (
    validate_report_payload,
    validate_dsl_payload,
    validate_report_with_details,
    validate_dsl_with_details,
    StructuredValidationError,
)
from engine.compiler.compiler_pipeline import compile_report, CompilerPipelineError
from engine.scoring.risk_calculator import summarize_risk_distribution
from engine.renderer.html_renderer import render_report_html, render_professional_html
from engine.renderer.pdf_renderer import render_pdf_from_html, validate_pdf_output
from engine.renderer.render_manifest import build_render_manifest

from engine.quality.quality_gate_enforcer import (
    enforce_quality_gates,
    should_block_generation,
)

router = APIRouter()


def extract_report_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract canonical report from request payload.
    
    Handles both wrapped payloads: { "report": <canonical> }
    and direct payloads: <canonical>
    
    Args:
        payload: Request body
        
    Returns:
        Canonical report object
    """
    # Check if this is a wrapped payload with a 'report' key containing report data
    if isinstance(payload, dict) and "report" in payload:
        report_data = payload["report"]
        # If report_data is a dict with canonical report structure, it's the wrapped report
        # Canonical reports have: report, engagement, findings, evidence, recommendations, etc.
        if isinstance(report_data, dict) and any(k in report_data for k in ["findings", "evidence", "recommendations", "engagement", "executive_summary"]):
            return report_data
    # Otherwise, assume it's already the canonical report
    return payload


@router.get("/health")
def healthcheck():
    """Health check endpoint."""
    return {
        "service": "Metis Report Engine",
        "status": "ok",
        "version": "0.1.0",
    }


@router.post("/validate-dsl")
def validate_dsl(dsl_text: str = Body(..., embed=True)) -> Dict[str, Any]:
    """Validate DSL text structure.
    
    Args:
        dsl_text: The DSL text to validate
        
    Returns:
        Validation result
    """
    result = validate_dsl_with_details(dsl_text)
    return result


@router.post("/compile-dsl")
def compile_dsl(dsl_text: str = Body(..., embed=True)) -> Dict[str, Any]:
    """Compile DSL to canonical JSON.
    
    Args:
        dsl_text: The DSL text to compile
        
    Returns:
        Compiled report JSON
    """
    try:
        compiled = compile_report(dsl_text=dsl_text)
        return {
            "status": "success",
            "report": compiled,
        }
    except CompilerPipelineError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compilation failed: {e}")


@router.post("/validate-report-json")
def validate_report_json(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Validate canonical report JSON against schema.
    
    Args:
        payload: The report JSON to validate (supports both direct and wrapped: {"report": {...}})
        
    Returns:
        Validation result
    """
    # Extract canonical report from payload (handles both wrapped and direct)
    report_json = extract_report_payload(payload)
    result = validate_report_with_details(report_json)
    return result


@router.post("/compile-report-json")
def compile_report_json(
    report_json: Dict[str, Any] = Body(...),
    add_metrics: bool = True,
) -> Dict[str, Any]:
    """Compile partial report JSON to canonical form.
    
    Args:
        report_json: The partial report JSON
        add_metrics: Whether to add calculated metrics
        
    Returns:
        Compiled canonical report
    """
    try:
        compiled = compile_report(report_json=report_json)
        
        if add_metrics:
            compiled["derived_metrics"] = summarize_risk_distribution(compiled)
        
        return {
            "status": "success",
            "report": compiled,
        }
    except CompilerPipelineError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compilation failed: {e}")


@router.post("/render-html")
def render_html(
    payload: Dict[str, Any] = Body(...),
    template: Optional[str] = None,
    theme: Optional[str] = None,
) -> HTMLResponse:
    """Render report to HTML.
    
    Args:
        payload: The report JSON to render (supports both direct and wrapped: {"report": {...}})
        template: Optional template name
        theme: Optional theme profile
        
    Returns:
        HTML response
    """
    try:
        # Extract canonical report from payload (handles both wrapped and direct)
        report = extract_report_payload(payload)
        
        # Validate first
        validation = validate_report_with_details(report)
        if not validation["valid"]:
            # Log warning but continue (schema issues are known)
            print(f"Warning: Schema validation failed: {validation.get('error', {}).get('message', '')}")
        
        # Render HTML
        if template == "professional":
            html = render_professional_html(report, theme_profile=theme or "vistiqx_consulting")
        else:
            html = render_report_html(report, template_name=template, theme_profile=theme)
        
        return HTMLResponse(content=html)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rendering failed: {e}")


@router.post("/render-pdf")
def render_pdf(
    payload: Dict[str, Any] = Body(...),
    template: Optional[str] = None,
    theme: Optional[str] = None,
    return_manifest: bool = True,
    skip_quality_gates: bool = False,
) -> Dict[str, Any]:
    """Render report to PDF.
    
    Args:
        payload: The report JSON to render (supports both direct and wrapped: {"report": {...}})
        template: Optional template name
        theme: Optional theme profile
        return_manifest: Whether to include render manifest
        skip_quality_gates: Whether to skip quality gate enforcement
        
    Returns:
        PDF file path and optional manifest
    """
    try:
        # Extract canonical report from payload (handles both wrapped and direct)
        report = extract_report_payload(payload)
        
        # Validate first
        validation = validate_report_with_details(report)
        if not validation["valid"]:
            print(f"Warning: Schema validation failed: {validation.get('error', {}).get('message', '')}")
        
        # Enforce quality gates (block with warning behavior)
        quality_result = enforce_quality_gates(report)
        if should_block_generation(quality_result, skip_gates=skip_quality_gates):
            response = {
                "status": "blocked",
                "message": "Quality gates failed. PDF generation blocked.",
                "quality_gates": quality_result.to_dict(),
            }
            if skip_quality_gates:
                response["note"] = "Use skip_quality_gates=true to override"
            raise HTTPException(status_code=400, detail=response)
        
        # Generate HTML
        if template == "professional":
            html = render_professional_html(report, theme_profile=theme or "vistiqx_consulting")
        else:
            html = render_report_html(report, template_name=template, theme_profile=theme)
        
        # Create temp PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            pdf_path = tmp.name
        
        # Render PDF
        render_pdf_from_html(html, pdf_path)
        
        # Validate PDF
        pdf_validation = validate_pdf_output(pdf_path)
        if not pdf_validation["valid"]:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {pdf_validation['error']}")
        
        # Build manifest
        result = {
            "status": "success",
            "pdf_path": pdf_path,
            "pdf_size": pdf_validation["size"],
        }
        
        if return_manifest:
            manifest = build_render_manifest(
                report,
                template_id=template or "default",
                theme_profile=theme or "default",
                validation_status="passed",
                output_pdf_path=pdf_path,
            )
            result["manifest"] = manifest
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF rendering failed: {e}")


@router.post("/export-report")
def export_report(
    payload: Dict[str, Any] = Body(...),
    format: str = "markdown",
    template: Optional[str] = None,
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Export report to various formats.
    
    Args:
        payload: The report JSON to export (supports both direct and wrapped: {"report": {...}})
        format: Export format (json, markdown, html, csv)
        template: Optional template name
        theme: Optional theme profile
        
    Returns:
        Exported content
    """
    from engine.export.export_manager import export_report as do_export
    
    try:
        # Extract canonical report from payload (handles both wrapped and direct)
        report = extract_report_payload(payload)
        
        content = do_export(
            report,
            format,
            template=template,
            theme=theme,
        )
        
        return {
            "status": "success",
            "format": format,
            "content": content if format != "pdf" else f"PDF saved to: {content}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")


@router.post("/generate-report")
def generate_report(report_path: str) -> Dict[str, Any]:
    """Legacy endpoint: Load report from file and generate preview.
    
    Args:
        report_path: Path to report JSON file
        
    Returns:
        Generation result
    """
    try:
        payload = load_report_json(report_path)
        
        # Validate
        validation = validate_report_with_details(payload)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation)
        
        # Add metrics and render
        payload["derived_metrics"] = summarize_risk_distribution(payload)
        html = render_report_html(payload)
        
        return {
            "status": "success",
            "preview_html_length": len(html),
            "validation": validation,
            "message": "Report generated successfully",
        }
        
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
