"""Integration tests for the complete application."""

from datetime import date

import pytest
from django.test import TransactionTestCase
from fastapi.testclient import TestClient
from wagtail.models import Page, Site
from wagtail.rich_text import RichText

from blog.models import BlogPage
from main_asgi import app as fastapi_app


@pytest.mark.integration
@pytest.mark.django_db
class TestBlogAPIIntegration(TransactionTestCase):
    """Integration tests for blog API with real database."""

    def setUp(self):
        """Set up test data."""
        # Create default locale if it doesn't exist
        try:
            from wagtail.models import Locale
        except ImportError:
            from wagtail.core.models import Locale

        # Ensure a default locale exists
        try:
            default_locale = Locale.objects.get(language_code="en")
        except Locale.DoesNotExist:
            default_locale = Locale.objects.create(language_code="en")

        # Set as default locale if not already set
        if not Locale.objects.filter(language_code="en").exists():
            default_locale = Locale.objects.create(language_code="en")
        else:
            default_locale = Locale.objects.get(language_code="en")

        # Create root page if it doesn't exist
        try:
            self.root_page = Page.objects.get(title="Root")
        except Page.DoesNotExist:
            self.root_page = Page.add_root(title="Root", slug="root")

        # Ensure the root page has a locale
        if hasattr(self.root_page, "locale"):
            if not self.root_page.locale:
                self.root_page.locale = default_locale
                self.root_page.save()

        # Create default site if it doesn't exist
        if not Site.objects.exists():
            Site.objects.create(
                hostname="localhost",
                port=80,
                root_page=self.root_page,
                is_default_site=True,
            )

        # Create test blog posts
        self.blog_posts = []
        for i in range(3):
            blog_page = BlogPage(
                title=f"Test Blog Post {i + 1}",
                intro=f"This is test intro {i + 1}",
                body=RichText(f"<p>This is test content {i + 1}</p>"),
                slug=f"test-blog-post-{i + 1}",
                date=date.today(),  # Add required date field
                live=True,
            )
            # Set locale if the field exists
            if hasattr(blog_page, "locale"):
                blog_page.locale = default_locale

            self.root_page.add_child(instance=blog_page)
            blog_page.save()
            self.blog_posts.append(blog_page)

    def test_complete_blog_api_flow(self):
        """Test complete blog API flow with real data."""
        client = TestClient(fastapi_app)

        # Test health check
        response = client.get("/api/posts/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["total_posts"] == 3

        # Test posts list
        response = client.get("/api/posts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["posts"]) == 3
        assert data["pagination"]["total_count"] == 3

        # Test individual post
        post_id = self.blog_posts[0].id
        response = client.get(f"/api/posts/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Blog Post 1"
        assert data["intro"] == "This is test intro 1"

        # Test pagination
        response = client.get("/api/posts/?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["posts"]) == 2
        assert data["pagination"]["has_next"] is True

        response = client.get("/api/posts/?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["posts"]) == 1
        assert data["pagination"]["has_next"] is False

    def test_blog_api_search_functionality(self):
        """Test blog API search functionality."""
        client = TestClient(fastapi_app)

        # Test search (currently returns all posts but verifies API structure)
        response = client.get("/api/posts/?search=test")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "meta" in data
        assert data["meta"]["search_query"] == "test"

    def test_blog_api_caching(self):
        """Test blog API caching functionality."""
        client = TestClient(fastapi_app)

        # Clear cache first
        response = client.post("/api/posts/cache/clear")
        assert response.status_code == 200

        # Check initial cache stats
        response = client.get("/api/posts/stats")
        assert response.status_code == 200
        initial_stats = response.json()
        assert initial_stats["cache"]["hits"] == 0
        assert initial_stats["cache"]["misses"] == 0


@pytest.mark.integration
@pytest.mark.django_db
class TestPaymentAPIIntegration(TransactionTestCase):
    """Integration tests for payment API."""

    def setUp(self):
        """Set up test data."""
        pass

    def test_payment_validation_integration(self):
        """Test payment validation in integration context."""
        client = TestClient(fastapi_app)

        # Test invalid amount
        invalid_data = {
            "article_id": 1,
            "amount": -100,
            "article_title": "Test Article",
            "success_url": "http://localhost:8000/success/",
            "cancel_url": "http://localhost:8000/cancel/",
        }

        response = client.post(
            "/api/payments/create-checkout-session", json=invalid_data
        )
        assert response.status_code == 400

        # Test invalid URL domain
        invalid_url_data = {
            "article_id": 1,
            "amount": 500,
            "article_title": "Test Article",
            "success_url": "http://malicious.com/success/",
            "cancel_url": "http://localhost:8000/cancel/",
        }

        response = client.post(
            "/api/payments/create-checkout-session", json=invalid_url_data
        )
        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.django_db
class TestFullApplicationIntegration(TransactionTestCase):
    """Integration tests for the complete application stack."""

    def setUp(self):
        """Set up test data."""
        pass

    def test_django_fastapi_integration(self):
        """Test Django and FastAPI integration."""
        client = TestClient(fastapi_app)

        # Test that FastAPI can access Django models
        response = client.get("/api/posts/debug")
        assert response.status_code == 200
        data = response.json()
        assert "sync_count" in data
        assert "async_count" in data
        assert data["status"] == "ok"

    def test_error_handling_integration(self):
        """Test error handling across the application."""
        client = TestClient(fastapi_app)

        # Test 404 for non-existent post
        response = client.get("/api/posts/99999")
        assert response.status_code == 404

        # Test 422 for invalid input
        response = client.get("/api/posts/?limit=999")
        assert response.status_code == 422
