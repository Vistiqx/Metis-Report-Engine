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

router = APIRouter()


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
def validate_report_json(report_json: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Validate canonical report JSON against schema.
    
    Args:
        report_json: The report JSON to validate
        
    Returns:
        Validation result
    """
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
    report_json: Dict[str, Any] = Body(...),
    template: Optional[str] = None,
    theme: Optional[str] = None,
) -> HTMLResponse:
    """Render report to HTML.
    
    Args:
        report_json: The report JSON to render
        template: Optional template name
        theme: Optional theme profile
        
    Returns:
        HTML response
    """
    try:
        # Validate first
        validation = validate_report_with_details(report_json)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation)
        
        # Render HTML
        if template == "professional":
            html = render_professional_html(report_json, theme_profile=theme or "vistiqx_consulting")
        else:
            html = render_report_html(report_json, template_name=template, theme_profile=theme)
        
        return HTMLResponse(content=html)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rendering failed: {e}")


@router.post("/render-pdf")
def render_pdf(
    report_json: Dict[str, Any] = Body(...),
    template: Optional[str] = None,
    theme: Optional[str] = None,
    return_manifest: bool = True,
) -> Dict[str, Any]:
    """Render report to PDF.
    
    Args:
        report_json: The report JSON to render
        template: Optional template name
        theme: Optional theme profile
        return_manifest: Whether to include render manifest
        
    Returns:
        PDF file path and optional manifest
    """
    try:
        # Validate first
        validation = validate_report_with_details(report_json)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation)
        
        # Generate HTML
        if template == "professional":
            html = render_professional_html(report_json, theme_profile=theme or "vistiqx_consulting")
        else:
            html = render_report_html(report_json, template_name=template, theme_profile=theme)
        
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
                report_json,
                template_id=template or "default",
                theme_profile=theme or "default",
                validation_status="passed",
                output_pdf_path=pdf_path,
            )
            result["manifest"] = manifest
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF rendering failed: {e}")


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
