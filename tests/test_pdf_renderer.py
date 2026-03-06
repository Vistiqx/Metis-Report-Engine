"""Tests for PDF renderer module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from engine.renderer.pdf_renderer import (
    render_pdf_from_html,
    render_report_to_pdf,
    validate_pdf_output,
    PDFRenderError,
)


class TestRenderPDFFromHTML:
    """Test PDF rendering from HTML."""
    
    @patch("engine.renderer.pdf_renderer.sync_playwright")
    def test_render_basic_pdf(self, mock_playwright):
        # Setup mock
        mock_context = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.__enter__ = Mock(return_value=mock_context)
        mock_context.chromium = Mock()
        mock_context.chromium.launch = Mock(return_value=mock_browser)
        mock_browser.new_page = Mock(return_value=mock_page)
        
        html = "<html><body><h1>Test</h1></body></html>"
        output_path = "test_output/test.pdf"
        
        result = render_pdf_from_html(html, output_path)
        
        assert result == output_path
        mock_page.set_content.assert_called_once()
        mock_page.pdf.assert_called_once()
        mock_browser.close.assert_called_once()
    
    @patch("engine.renderer.pdf_renderer.sync_playwright")
    def test_render_with_custom_margins(self, mock_playwright):
        mock_context = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.__enter__ = Mock(return_value=mock_context)
        mock_context.chromium.launch = Mock(return_value=mock_browser)
        mock_browser.new_page = Mock(return_value=mock_page)
        
        html = "<html><body>Test</body></html>"
        output_path = "test.pdf"
        custom_margin = {"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"}
        
        render_pdf_from_html(html, output_path, margin=custom_margin)
        
        # Check PDF was called with custom margin
        call_args = mock_page.pdf.call_args
        assert call_args.kwargs["margin"] == custom_margin
    
    @patch("engine.renderer.pdf_renderer.sync_playwright")
    def test_render_with_landscape(self, mock_playwright):
        mock_context = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.__enter__ = Mock(return_value=mock_context)
        mock_context.chromium.launch = Mock(return_value=mock_browser)
        mock_browser.new_page = Mock(return_value=mock_page)
        
        html = "<html><body>Test</body></html>"
        output_path = "test.pdf"
        
        render_pdf_from_html(html, output_path, landscape=True)
        
        call_args = mock_page.pdf.call_args
        assert call_args.kwargs["landscape"] is True
    
    @patch("engine.renderer.pdf_renderer.sync_playwright")
    def test_render_creates_output_directory(self, mock_playwright, tmp_path):
        mock_context = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.__enter__ = Mock(return_value=mock_context)
        mock_context.chromium.launch = Mock(return_value=mock_browser)
        mock_browser.new_page = Mock(return_value=mock_page)
        
        html = "<html><body>Test</body></html>"
        output_dir = tmp_path / "nested" / "dir"
        output_path = output_dir / "test.pdf"
        
        render_pdf_from_html(html, str(output_path))
        
        # Directory should be created
        assert output_dir.exists()


class TestRenderReportToPDF:
    """Test rendering report JSON to PDF."""
    
    @patch("engine.renderer.pdf_renderer.render_pdf_from_html")
    def test_render_report_calls_html_renderer(self, mock_render_pdf):
        report_json = {"report": {"id": "RPT-001", "title": "Test"}}
        mock_html_renderer = Mock(return_value="<html>Test</html>")
        output_path = "test.pdf"
        
        render_report_to_pdf(report_json, mock_html_renderer, output_path)
        
        mock_html_renderer.assert_called_once_with(report_json)
        mock_render_pdf.assert_called_once()
    
    @patch("engine.renderer.pdf_renderer.render_pdf_from_html")
    def test_render_report_passes_options(self, mock_render_pdf):
        report_json = {"report": {"id": "RPT-001"}}
        mock_html_renderer = Mock(return_value="<html>Test</html>")
        output_path = "test.pdf"
        
        render_report_to_pdf(
            report_json,
            mock_html_renderer,
            output_path,
            page_size="Letter",
            landscape=True,
        )
        
        call_args = mock_render_pdf.call_args
        assert call_args.kwargs["page_size"] == "Letter"
        assert call_args.kwargs["landscape"] is True


class TestValidatePDFOutput:
    """Test PDF validation."""
    
    def test_valid_pdf_file(self, tmp_path):
        pdf_file = tmp_path / "test.pdf"
        # Create a minimal valid PDF
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        pdf_file.write_bytes(pdf_content)
        
        result = validate_pdf_output(str(pdf_file))
        
        assert result["valid"] is True
        assert result["exists"] is True
        assert result["size"] > 0
        assert result["error"] is None
    
    def test_nonexistent_file(self):
        result = validate_pdf_output("/nonexistent/path/file.pdf")
        
        assert result["valid"] is False
        assert result["exists"] is False
        assert "does not exist" in result["error"]
    
    def test_empty_file(self, tmp_path):
        empty_file = tmp_path / "empty.pdf"
        empty_file.write_text("")
        
        result = validate_pdf_output(str(empty_file))
        
        assert result["valid"] is False
        assert result["exists"] is True
        assert "empty" in result["error"]
    
    def test_invalid_pdf_header(self, tmp_path):
        invalid_file = tmp_path / "invalid.pdf"
        invalid_file.write_text("This is not a PDF file")
        
        result = validate_pdf_output(str(invalid_file))
        
        assert result["valid"] is False
        assert result["exists"] is True
        assert "not a valid PDF" in result["error"]


class TestPDFRenderError:
    """Test PDF render error handling."""
    
    def test_error_includes_message(self):
        error = PDFRenderError("Test error message")
        
        assert "Test error message" in str(error)
