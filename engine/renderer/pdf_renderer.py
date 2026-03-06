from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright


def render_pdf_from_html(html: str, output_path: str | Path) -> str:
    output = str(output_path)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.pdf(path=output, print_background=True)
        browser.close()
    return output
