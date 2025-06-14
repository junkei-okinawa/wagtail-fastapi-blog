"""Test configuration and fixtures."""

import os
import pytest
from django.conf import settings
from django.test import override_settings
from httpx import AsyncClient
import django
from fastapi.testclient import TestClient

# Django設定の初期化
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.totonoe_template.settings.test")

# テスト用のDjango設定オーバーライド
if not settings.configured:
    django.setup()

from main_asgi import app as fastapi_app


@pytest.fixture
def client():
    """FastAPI test client."""
    with override_settings(
        DEBUG=True,
        ALLOWED_HOSTS=['*'],  # テスト環境では全てのホストを許可
        USE_TZ=False,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
    ):
        return TestClient(fastapi_app)


@pytest.fixture
async def async_client():
    """Async HTTP client for FastAPI testing."""
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_stripe_key(monkeypatch):
    """Mock Stripe API key for testing."""
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_mock_key")
    monkeypatch.setenv("STRIPE_PUBLIC_KEY", "pk_test_mock_key")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_secret")


@pytest.fixture
def sample_blog_data():
    """Sample blog post data for testing."""
    return {
        "article_id": 1,
        "amount": 500,
        "article_title": "Test Article Title",
        "success_url": "http://localhost:8000/success/",
        "cancel_url": "http://localhost:8000/cancel/"
    }
