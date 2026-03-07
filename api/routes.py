"""API routes for Metis Report Engine.

Implements endpoints per API_CONTRACT.md:
- GET /health
- POST /validate-dsl
- POST /compile-dsl
- POST /validate-report-json
- POST /render-html
- POST /render-pdf
"""

from fastapi import APIRouter, HTTPException, Body, Query
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from typing import Any, Dict, Optional
from pathlib import Path
import tempfile
import json
import os
import logging

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
from engine.renderer.renderer_selector import (
    detect_schema_version,
    select_renderer,
    log_render_selection,
)
from engine.renderer.v2_transformer import transform_v2_to_template_context

from engine.quality.quality_gate_enforcer import (
    enforce_quality_gates,
    should_block_generation,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Artifact directory for PDF storage
ARTIFACT_DIR = Path(tempfile.gettempdir()) / "metis_artifacts"
ARTIFACT_DIR.mkdir(exist_ok=True)

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
    return_type: str = Query("file", description="Return type: 'file' (default) returns PDF directly, 'metadata' returns JSON with download URL"),
    skip_quality_gates: bool = False,
):
    """Render report to PDF with automatic schema version detection.
    
    Automatically selects consulting-grade renderer for schema v2 reports
    and legacy renderer for schema v1 reports.
    
    Args:
        payload: The report JSON to render (supports both direct and wrapped: {"report": {...}})
        template: Optional template name (overrides auto-selection)
        theme: Optional theme profile (overrides auto-selection)
        return_type: "file" returns PDF directly (default), "metadata" returns JSON with artifact URL
        skip_quality_gates: Whether to skip quality gate enforcement
        
    Returns:
        PDF file (default) or metadata JSON with artifact URL
    """
    try:
        logger.info("=" * 60)
        logger.info("PDF RENDER ENDPOINT INVOKED")
        logger.info("=" * 60)
        
        # Extract canonical report from payload (handles both wrapped and direct)
        report = extract_report_payload(payload)
        
        # Detect schema version and log it
        schema_version = detect_schema_version(report)
        renderer_config = select_renderer(report)
        
        logger.info(f"[RENDER-PDF] Detected schema version: {schema_version}")
        logger.info(f"[RENDER-PDF] Renderer selected: {renderer_config['renderer']}")
        logger.info(f"[RENDER-PDF] Template selected: {renderer_config['template']}")
        
        # Validate first
        validation = validate_report_with_details(report)
        if not validation["valid"]:
            logger.warning(f"[RENDER-PDF] Schema validation failed: {validation.get('error', {}).get('message', '')}")
        
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
        
        # Determine template and theme (explicit overrides auto-selection)
        if template:
            actual_template = template
            logger.info(f"[RENDER-PDF] Using explicit template: {actual_template}")
        else:
            actual_template = renderer_config["template"]
            logger.info(f"[RENDER-PDF] Using auto-selected template for schema v{schema_version}: {actual_template}")
        
        actual_theme = theme or renderer_config["theme"]
        logger.info(f"[RENDER-PDF] Using theme: {actual_theme}")
        
        # Generate HTML with automatic renderer selection based on schema version
        logger.info(f"[RENDER-PDF] Generating HTML...")
        html = render_report_html(report, template_name=actual_template, theme_profile=actual_theme)
        logger.info(f"[RENDER-PDF] HTML generated: {len(html)} bytes")
        
        # Generate safe filename
        report_id = report.get("report", {}).get("id", "report")
        report_title = report.get("report", {}).get("title", "untitled")
        safe_filename = f"{report_id}_{report_title[:50]}.pdf".replace(" ", "_").replace("/", "_")
        
        # Save to artifact directory
        pdf_path = ARTIFACT_DIR / safe_filename
        logger.info(f"[RENDER-PDF] Rendering PDF to: {pdf_path}")
        render_pdf_from_html(html, pdf_path)
        logger.info(f"[RENDER-PDF] PDF saved successfully")
        
        # Validate PDF
        pdf_validation = validate_pdf_output(pdf_path)
        if not pdf_validation["valid"]:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {pdf_validation['error']}")
        
        logger.info(f"[RENDER-PDF] PDF validation passed: {pdf_validation['size']} bytes")
        logger.info("=" * 60)
        
        # Return based on requested type
        if return_type == "metadata":
            # Build enhanced manifest with renderer info
            manifest = build_render_manifest(
                report,
                template_id=actual_template,
                theme_profile=actual_theme,
                validation_status="passed",
                output_pdf_path=str(pdf_path),
            )
            # Add renderer info to manifest
            manifest["renderer_info"] = {
                "schema_version": schema_version,
                "renderer": renderer_config["renderer"],
                "template": actual_template,
                "theme": actual_theme,
            }
            
            return {
                "status": "success",
                "artifact_url": f"/artifacts/{safe_filename}",
                "filename": safe_filename,
                "pdf_size": pdf_validation["size"],
                "schema_version": schema_version,
                "renderer": renderer_config["renderer"],
                "template": actual_template,
                "manifest": manifest,
            }
        else:
            # Return PDF file directly (default)
            return FileResponse(
                path=pdf_path,
                media_type="application/pdf",
                filename=safe_filename,
            )
        
    except Exception as e:
        logger.error(f"[RENDER-PDF] Error: {e}")
        raise HTTPException(status_code=500, detail=f"PDF rendering failed: {e}")


@router.get("/artifacts/{filename}")
def get_artifact(filename: str):
    """Retrieve a generated PDF artifact by filename.
    
    Args:
        filename: The artifact filename
        
    Returns:
        PDF file
    """
    # Validate filename (prevent directory traversal)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    artifact_path = ARTIFACT_DIR / filename
    
    # Check if file exists
    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Return PDF
    return FileResponse(
        path=artifact_path,
        media_type="application/pdf",
        filename=filename,
    )


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
