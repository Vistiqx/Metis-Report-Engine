from fastapi import APIRouter, HTTPException
from engine.parser.report_loader import load_report_json
from engine.parser.schema_validator import validate_report_payload
from engine.scoring.risk_calculator import summarize_risk_distribution
from engine.renderer.html_renderer import render_report_html

router = APIRouter()


@router.get("/")
def healthcheck():
    return {"service": "Metis Report Engine", "status": "ok"}


@router.post("/generate-report")
def generate_report(report_path: str):
    try:
        payload = load_report_json(report_path)
        validate_report_payload(payload)
        payload["derived_metrics"] = summarize_risk_distribution(payload)
        html = render_report_html(payload)
        return {
            "status": "success",
            "preview_html_length": len(html),
            "message": "HTML render completed. PDF export to be handled by renderer pipeline."
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
