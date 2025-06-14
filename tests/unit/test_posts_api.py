"""Unit tests for FastAPI posts router."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

# テスト用のモックデータ
@pytest.mark.unit
class TestPostsRouter:
    """Test posts API router functionality."""
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        with patch('fastapi_app.app.routers.posts.get_blog_pages_count') as mock_count:
            mock_count.return_value = 5
            
            response = client.get("/api/posts/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["total_posts"] == 5
            assert "execution_time" in data
            assert "timestamp" in data
    
    def test_performance_stats_endpoint(self, client):
        """Test performance stats endpoint."""
        with patch('fastapi_app.app.routers.posts._get_cached_blog_pages') as mock_cache:
            # Mock cache_info method
            mock_cache_info = MagicMock()
            mock_cache_info.hits = 5
            mock_cache_info.misses = 2
            mock_cache_info.currsize = 3
            mock_cache_info.maxsize = 128
            mock_cache.cache_info.return_value = mock_cache_info
            
            response = client.get("/api/posts/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert "cache" in data
            assert "timestamp" in data
            assert data["cache"]["hits"] == 5
            assert data["cache"]["misses"] == 2
            assert data["cache"]["hit_rate"] == 5 / (5 + 2)  # 0.714...
    
    def test_posts_count_endpoint(self, client):
        """Test posts count endpoint."""
        with patch('fastapi_app.app.routers.posts.get_blog_pages_count') as mock_count:
            mock_count.return_value = 3
            
            response = client.get("/api/posts/count")
            
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 3
    
    def test_cache_clear_endpoint(self, client):
        """Test cache clear endpoint."""
        response = client.post("/api/posts/cache/clear")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Cache cleared successfully"
        assert "execution_time" in data
    
    def test_debug_endpoint(self, client):
        """Test debug endpoint."""
        with patch('blog.models.BlogPage.objects') as mock_objects:
            mock_objects.live.return_value.public.return_value.count.return_value = 2
            
            with patch('fastapi_app.app.routers.posts.get_blog_pages_count') as mock_async_count:
                mock_async_count.return_value = 2
                
                response = client.get("/api/posts/debug")
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"
                assert data["sync_count"] == 2
                assert data["async_count"] == 2


@pytest.mark.unit
@pytest.mark.django_db 
class TestPostsAPIValidation:
    """Test posts API input validation and error handling."""
    
    def test_list_posts_pagination_validation(self, client):
        """Test posts list endpoint with pagination parameters."""
        with patch('fastapi_app.app.routers.posts.get_blog_pages_count') as mock_count:
            mock_count.return_value = 10
            
            with patch('fastapi_app.app.routers.posts.get_blog_pages_optimized') as mock_get_posts:
                mock_get_posts.return_value = []
                
                # Test valid pagination
                response = client.get("/api/posts/?limit=5&offset=0")
                assert response.status_code == 200
                
                # Test limit validation
                response = client.get("/api/posts/?limit=150")  # Over max limit
                assert response.status_code == 422
                
                # Test negative offset
                response = client.get("/api/posts/?offset=-1")
                assert response.status_code == 422
    
    def test_get_post_by_id_not_found(self, client):
        """Test get post by ID when post doesn't exist."""
        with patch('fastapi_app.app.routers.posts.get_blog_page_by_id_optimized') as mock_get:
            mock_get.return_value = None
            
            response = client.get("/api/posts/999")
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Post not found"
