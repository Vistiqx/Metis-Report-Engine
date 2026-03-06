"""PDF renderer for Metis Report Engine.

This module provides robust PDF generation from HTML using Playwright.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class PDFRenderError(Exception):
    """Raised when PDF rendering fails."""
    pass


def render_pdf_from_html(
    html: str,
    output_path: str | Path,
    *,
    page_size: str = "A4",
    landscape: bool = False,
    margin: Optional[Dict[str, str]] = None,
    print_background: bool = True,
    wait_for_load: bool = True,
    timeout: int = 30000,
) -> str:
    """Render HTML to PDF using Playwright.

    Args:
        html: The HTML content to render
        output_path: Path where the PDF should be saved
        page_size: Page size (A4, Letter, Legal, etc.)
        landscape: Whether to use landscape orientation
        margin: Margins as dict with top, right, bottom, left keys
        print_background: Whether to print background graphics
        wait_for_load: Whether to wait for page load
        timeout: Timeout in milliseconds

    Returns:
        Path to the generated PDF file

    Raises:
        PDFRenderError: If rendering fails
    """
    output = str(output_path)
    
    # Ensure output directory exists
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    
    # Default margins
    if margin is None:
        margin = {"top": "18mm", "right": "14mm", "bottom": "18mm", "left": "14mm"}
    
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            
            # Set content
            if wait_for_load:
                page.set_content(html, wait_until="networkidle")
            else:
                page.set_content(html)
            
            # Generate PDF
            page.pdf(
                path=output,
                format=page_size,
                landscape=landscape,
                margin=margin,
                print_background=print_background,
                timeout=timeout,
            )
            
            browser.close()
            
    except PlaywrightTimeout:
        raise PDFRenderError(f"PDF generation timed out after {timeout}ms")
    except Exception as e:
        raise PDFRenderError(f"PDF generation failed: {e}")
    
    return output


def render_report_to_pdf(
    report_json: Dict[str, Any],
    html_renderer: callable,
    output_path: str | Path,
    **pdf_options,
) -> str:
    """Render a report JSON directly to PDF.

    Args:
        report_json: The canonical report JSON
        html_renderer: Function that takes report_json and returns HTML string
        output_path: Path where the PDF should be saved
        **pdf_options: Additional options for render_pdf_from_html

    Returns:
        Path to the generated PDF file
    """
    # Generate HTML from report
    html = html_renderer(report_json)
    
    # Render PDF
    return render_pdf_from_html(html, output_path, **pdf_options)


def validate_pdf_output(pdf_path: str | Path) -> Dict[str, Any]:
    """Validate that a PDF file was generated correctly.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Validation result with status and file info
    """
    path = Path(pdf_path)
    
    result = {
        "valid": False,
        "exists": False,
        "size": 0,
        "error": None,
    }
    
    try:
        if not path.exists():
            result["error"] = "File does not exist"
            return result
        
        result["exists"] = True
        
        # Check file size
        size = path.stat().st_size
        result["size"] = size
        
        if size == 0:
            result["error"] = "File is empty"
            return result
        
        # Basic PDF header check
        with open(path, "rb") as f:
            header = f.read(5)
            if header != b"%PDF-":
                result["error"] = "File is not a valid PDF"
                return result
        
        result["valid"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result
