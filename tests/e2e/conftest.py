"""Playwright fixtures for E2E testing with dev server."""

import pytest
import subprocess
import time
import socket
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser


@pytest.fixture(scope="session")
def dev_server():
    """Connect to existing FastAPI dev server or start new one.
    
    Yields:
        str: Base URL of the running server (e.g., http://localhost:8000)
    """
    # Check if server is already running on port 8000
    base_url = "http://localhost:8000"
    try:
        import urllib.request
        urllib.request.urlopen(f"{base_url}/health", timeout=2)
        print(f"Using existing server at {base_url}")
        yield base_url
        return
    except:
        pass
    
    # Start new server if not running
    import tempfile
    temp_dir = tempfile.mkdtemp()
    log_file = os.path.join(temp_dir, "server.log")
    
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=open(log_file, "w"),
        stderr=subprocess.STDOUT,
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
        with open(log_file) as f:
            log_content = f.read()
        raise RuntimeError(f"Server failed to start within {max_wait} seconds. Log:\n{log_content}")
    
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
