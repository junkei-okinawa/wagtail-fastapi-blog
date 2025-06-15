"""E2E test configuration and fixtures."""

try:
    import asyncio
    import os
    import subprocess
    import time

    import pytest
    import requests

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    pytest = None

if not PLAYWRIGHT_AVAILABLE:
    pytest.skip("Playwright not installed", allow_module_level=True)


def wait_for_server(url, timeout=30):
    """Wait for server to be available."""
    print(f"Waiting for server at {url} (timeout: {timeout}s)")
    start_time = time.time()
    attempt = 0
    while time.time() - start_time < timeout:
        attempt += 1
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"Server is ready after {attempt} attempts!")
                return True
            else:
                print(
                    f"Attempt {attempt}: Server returned status {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt}: Connection failed: {e}")
        time.sleep(2)  # Wait 2 seconds between attempts
    print(f"Server failed to start within {timeout} seconds after {attempt} attempts")
    return False


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def dev_server():
    """Start development server for E2E tests."""
    from pathlib import Path

    server_url = "http://127.0.0.1:8001"
    project_root = Path(__file__).parent.parent.parent

    # Check if server is already running
    try:
        response = requests.get(server_url, timeout=2)
        if response.status_code == 200:
            print(f"Server already running at {server_url}")
            yield server_url
            return
    except requests.exceptions.RequestException:
        pass

    # Setup E2E database before starting server
    print("Setting up E2E database...")
    setup_script = project_root / "scripts" / "setup_e2e_db.py"
    subprocess.run(
        ["uv", "run", "python", str(setup_script)], cwd=project_root, check=True
    )

    # Start the development server
    print(f"Starting server at {server_url}")
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "django_project.totonoe_template.settings.e2e"
    env["TESTING"] = "true"  # FastAPI側でのテスト認識
    env["DEBUG"] = "true"  # FastAPI側でのデバッグモード
    env["E2E_TESTING"] = "true"  # E2E環境フラグ
    # CORS設定をより明示的に
    cors_origins = (
        f"http://localhost:8001,http://127.0.0.1:8001,"
        f"{server_url},http://localhost:3000"
    )
    env["CORS_ALLOWED_ORIGINS"] = cors_origins
    print(f"Setting CORS_ALLOWED_ORIGINS: {cors_origins}")

    # Redirect stdout/stderr to avoid blocking
    with open(project_root / "e2e_server.log", "w") as log_file:
        server_process = subprocess.Popen(
            [
                "uv",
                "run",
                "uvicorn",
                "main_asgi:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8001",  # Different port to avoid conflicts
                "--log-level",
                "warning",  # Reduce log verbosity
            ],
            cwd=str(project_root),
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )

    # Wait for server to start with proper health check
    if not wait_for_server(server_url, timeout=60):  # Increase timeout
        print("Server startup failed, checking logs...")
        log_path = project_root / "e2e_server.log"
        if log_path.exists():
            print("Server log output:")
            print(log_path.read_text())
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        raise RuntimeError("Server failed to start within timeout")

    print(f"Server started successfully at {server_url}")
    yield server_url

    # Cleanup
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
        server_process.wait()


@pytest.fixture(scope="session")
def browser():
    """Create browser instance for tests."""
    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()
    playwright.stop()


@pytest.fixture
def page(browser):
    """Create page instance for each test."""
    page = browser.new_page()
    yield page
    page.close()
