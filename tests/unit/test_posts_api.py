"""Unit tests for FastAPI posts router."""

import pytest
from unittest.mock import patch, MagicMock

# テスト用のモックデータ
@pytest.mark.unit
class TestPostsRouter:
    """Test posts API router functionality."""
    
    @pytest.mark.django_db
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        with patch('fastapi_app.app.routers.posts.get_blog_pages_count') as mock_count:
            mock_count.return_value = 0  # 単体テストではDBに実際のデータがない
            
            response = client.get("/api/posts/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["total_posts"] == 0  # モックした値に合わせる
            assert "timestamp" in data
    
    @pytest.mark.django_db
    def test_performance_stats_endpoint(self, client):
        """Test performance stats endpoint."""
        with patch('fastapi_app.app.routers.posts.get_blog_pages_count') as mock_count:
            mock_count.return_value = 10
            
            response = client.get("/api/posts/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_posts"] == 10
            assert "cache" in data
            assert "performance" in data
            assert data["cache"]["hits"] == 0
            assert data["cache"]["misses"] == 0
            assert data["performance"]["avg_response_time"] == 0.1
    
    @pytest.mark.django_db
    def test_posts_count_endpoint(self, client):
        """Test posts count via health endpoint."""
        with patch('fastapi_app.app.routers.posts.get_blog_pages_count') as mock_count:
            mock_count.return_value = 0  # 単体テストではDBに実際のデータがない
            
            response = client.get("/api/posts/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_posts"] == 0  # モックした値に合わせる
    
    def test_cache_clear_endpoint(self, client):
        """Test cache clear endpoint."""
        response = client.post("/api/posts/cache/clear")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Cache cleared successfully"
    
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
        # Mock the BlogPage.objects to avoid database access
        with patch('blog.models.BlogPage.objects') as mock_objects:
            # Mock the queryset chain
            mock_queryset = mock_objects.live.return_value.public.return_value
            mock_queryset.count.return_value = 10
            mock_queryset.order_by.return_value.__getitem__.return_value = []
            
            # Test valid pagination
            response = client.get("/api/posts/?limit=5&offset=0")
            assert response.status_code == 200
            data = response.json()
            assert "posts" in data
            assert "pagination" in data
            
            # Test limit validation
            response = client.get("/api/posts/?limit=150")  # Over max limit
            assert response.status_code == 422
            
            # Test negative offset
            response = client.get("/api/posts/?offset=-1")
            assert response.status_code == 422
    
    def test_get_post_by_id_not_found(self, client):
        """Test get post by ID when post doesn't exist."""
        with patch('fastapi_app.app.routers.posts.get_blog_page_by_id') as mock_get:
            mock_get.return_value = None
            
            response = client.get("/api/posts/999")
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Post not found"
