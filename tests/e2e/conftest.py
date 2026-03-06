"""Playwright fixtures for E2E testing with dev server."""

import pytest
import subprocess
import time
import socket
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser


def find_free_port():
    """Find a free port for the dev server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture(scope="session")
def dev_server():
    """Start the FastAPI dev server for testing.
    
    Yields:
        str: Base URL of the running server (e.g., http://localhost:8000)
    """
    port = find_free_port()
    base_url = f"http://localhost:{port}"
    
    # Start the server
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).resolve().parents[3]),
    )
    
    # Wait for server to start
    max_wait = 30
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            import urllib.request
            urllib.request.urlopen(f"{base_url}/health", timeout=1)
            break
        except:
            time.sleep(0.5)
    else:
        proc.terminate()
        raise RuntimeError(f"Server failed to start within {max_wait} seconds")
    
    yield base_url
    
    # Cleanup
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture(scope="session")
def browser():
    """Create a Playwright browser instance."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Create a new page for each test."""
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture
def console_logs(page):
    """Capture console logs from the page."""
    logs = []
    page.on("console", lambda msg: logs.append({
        "type": msg.type,
        "text": msg.text,
        "location": msg.location,
    }))
    return logs


@pytest.fixture
def page_errors(page):
    """Capture page errors."""
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    return errors
