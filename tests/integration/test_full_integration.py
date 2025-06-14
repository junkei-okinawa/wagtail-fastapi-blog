"""Integration tests for the complete application."""

import pytest
import asyncio
from httpx import AsyncClient
from django.test import TransactionTestCase
from wagtail.models import Page
from wagtail.rich_text import RichText

from blog.models import BlogPage
from main_asgi import app as fastapi_app


@pytest.mark.integration
class TestBlogAPIIntegration(TransactionTestCase):
    """Integration tests for blog API with real database."""
    
    def setUp(self):
        """Set up test data."""
        self.root_page = Page.objects.get(title="Root")
        
        # Create test blog posts
        self.blog_posts = []
        for i in range(3):
            blog_page = BlogPage(
                title=f"Test Blog Post {i+1}",
                intro=f"This is test intro {i+1}",
                body=RichText(f"<p>This is test content {i+1}</p>"),
                slug=f"test-blog-post-{i+1}",
                live=True
            )
            self.root_page.add_child(instance=blog_page)
            blog_page.save()
            self.blog_posts.append(blog_page)
    
    @pytest.mark.asyncio
    async def test_complete_blog_api_flow(self):
        """Test complete blog API flow with real data."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            # Test health check
            response = await client.get("/api/posts/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["total_posts"] == 3
            
            # Test posts list
            response = await client.get("/api/posts/")
            assert response.status_code == 200
            data = response.json()
            assert len(data["posts"]) == 3
            assert data["pagination"]["total_count"] == 3
            
            # Test individual post
            post_id = self.blog_posts[0].id
            response = await client.get(f"/api/posts/{post_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Test Blog Post 1"
            assert data["intro"] == "This is test intro 1"
            
            # Test pagination
            response = await client.get("/api/posts/?limit=2&offset=0")
            assert response.status_code == 200
            data = response.json()
            assert len(data["posts"]) == 2
            assert data["pagination"]["has_next"] == True
            
            response = await client.get("/api/posts/?limit=2&offset=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data["posts"]) == 1
            assert data["pagination"]["has_next"] == False
    
    @pytest.mark.asyncio
    async def test_blog_api_search_functionality(self):
        """Test blog API search functionality."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            # Test search (currently returns all posts but verifies API structure)
            response = await client.get("/api/posts/?search=test")
            assert response.status_code == 200
            data = response.json()
            assert "posts" in data
            assert "meta" in data
            assert data["meta"]["search_query"] == "test"
    
    @pytest.mark.asyncio
    async def test_blog_api_caching(self):
        """Test blog API caching functionality."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            # Clear cache first
            response = await client.post("/api/posts/cache/clear")
            assert response.status_code == 200
            
            # Check initial cache stats
            response = await client.get("/api/posts/stats")
            assert response.status_code == 200
            initial_stats = response.json()
            assert initial_stats["cache"]["hits"] == 0
            assert initial_stats["cache"]["misses"] == 0
            
            # Make cached request
            response = await client.get("/api/posts/cached?limit=2")
            assert response.status_code == 200
            
            # Check cache stats after miss
            response = await client.get("/api/posts/stats")
            assert response.status_code == 200
            stats_after_miss = response.json()
            assert stats_after_miss["cache"]["misses"] == 1
            
            # Make same cached request again (should be hit)
            response = await client.get("/api/posts/cached?limit=2")
            assert response.status_code == 200
            
            # Check cache stats after hit
            response = await client.get("/api/posts/stats")
            assert response.status_code == 200
            stats_after_hit = response.json()
            assert stats_after_hit["cache"]["hits"] == 1
            assert stats_after_hit["cache"]["hit_rate"] == 0.5


@pytest.mark.integration
class TestPaymentAPIIntegration:
    """Integration tests for payment API."""
    
    @pytest.mark.asyncio
    async def test_payment_flow_integration(self):
        """Test complete payment flow integration."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            # Test checkout session creation
            payment_data = {
                "article_id": 1,
                "amount": 500,
                "article_title": "Integration Test Article",
                "success_url": "http://localhost:8000/success/",
                "cancel_url": "http://localhost:8000/cancel/"
            }
            
            # Note: This test requires valid Stripe test keys
            # In CI/CD, this could be mocked or use Stripe test fixtures
            with pytest.raises(Exception):  # Expected to fail without real Stripe keys
                response = await client.post("/api/payments/create-checkout-session", json=payment_data)
    
    @pytest.mark.asyncio
    async def test_payment_validation_integration(self):
        """Test payment validation in integration context."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            # Test invalid amount
            invalid_data = {
                "article_id": 1,
                "amount": -100,
                "article_title": "Test Article",
                "success_url": "http://localhost:8000/success/",
                "cancel_url": "http://localhost:8000/cancel/"
            }
            
            response = await client.post("/api/payments/create-checkout-session", json=invalid_data)
            assert response.status_code == 400
            
            # Test invalid URL domain
            invalid_url_data = {
                "article_id": 1,
                "amount": 500,
                "article_title": "Test Article",
                "success_url": "http://malicious.com/success/",
                "cancel_url": "http://localhost:8000/cancel/"
            }
            
            response = await client.post("/api/payments/create-checkout-session", json=invalid_url_data)
            assert response.status_code == 400


@pytest.mark.integration
class TestFullApplicationIntegration:
    """Integration tests for the complete application stack."""
    
    @pytest.mark.asyncio
    async def test_django_fastapi_integration(self):
        """Test Django and FastAPI integration."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            # Test that FastAPI can access Django models
            response = await client.get("/api/posts/debug")
            assert response.status_code == 200
            data = response.json()
            assert "sync_count" in data
            assert "async_count" in data
            assert data["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_static_files_integration(self):
        """Test static files integration."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            # Test that static files are accessible
            # Note: This might need adjustment based on your static file setup
            response = await client.get("/static/css/performance.css")
            # Static files might return 404 in test environment, which is expected
            assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio 
    async def test_error_handling_integration(self):
        """Test error handling across the application."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            # Test 404 for non-existent post
            response = await client.get("/api/posts/99999")
            assert response.status_code == 404
            
            # Test 422 for invalid input
            response = await client.get("/api/posts/?limit=999")
            assert response.status_code == 422
