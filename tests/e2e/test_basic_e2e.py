"""Basic E2E tests for infrastructure validation."""

import pytest


@pytest.mark.e2e
def test_e2e_infrastructure():
    """Test that E2E infrastructure is properly set up."""
    # Test that pytest-playwright is available
    try:
        import playwright

        assert playwright is not None
    except ImportError:
        pytest.fail("Playwright not available")

    # Test that async support is available
    try:
        import pytest_asyncio

        assert pytest_asyncio is not None
    except ImportError:
        pytest.fail("pytest-asyncio not available")

    # Test that requests library is available
    try:
        import requests

        assert requests is not None
    except ImportError:
        pytest.fail("requests library not available")

    print("E2E infrastructure validation passed")


@pytest.mark.e2e
def test_server_startup_infrastructure(dev_server):
    """Test that E2E server startup infrastructure works."""
    assert dev_server is not None
    assert dev_server.startswith("http://")
    assert "127.0.0.1:8001" in dev_server
    print(f"E2E server infrastructure validated: {dev_server}")


@pytest.mark.e2e
def test_browser_infrastructure(page, dev_server):
    """Test that browser automation infrastructure works."""
    # Test basic browser functionality
    page.goto(dev_server, timeout=10000)
    page.wait_for_load_state("domcontentloaded")

    # Verify we can interact with the page
    title = page.title()
    assert title is not None

    # Verify we can get page content
    content = page.content()
    assert len(content) > 0

    print("Browser automation infrastructure validated")
