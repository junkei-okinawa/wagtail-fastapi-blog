#!/usr/bin/env python3
"""
Working Tests Demo - Django + FastAPI Blog Project

このスクリプトは現在正常に動作しているテストを実行します。
テスト環境の動作確認やAPI機能の検証に使用できます。

実行方法:
    uv run python working_tests_demo.py

動作確認項目:
- FastAPI health check endpoint
- Performance stats endpoint  
- Posts count endpoint

注意: データベース関連のテストは除外されています。
"""

import os
import django
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Django setup for testing
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.totonoe_template.settings.test")
os.environ['TESTING'] = 'true'

django.setup()

from main_asgi import app

def test_api_health():
    """Test API health endpoint - this should work."""
    client = TestClient(app)
    
    with patch('fastapi_app.app.routers.posts.get_blog_pages_count') as mock_count:
        mock_count.return_value = 5
        
        response = client.get("/api/posts/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["total_posts"] == 5
        print("✅ Health check test passed!")

def test_api_stats():
    """Test API stats endpoint - this should work.""" 
    client = TestClient(app)
    
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
        print("✅ Stats endpoint test passed!")

def test_api_count():
    """Test API count endpoint - this should work."""
    client = TestClient(app)
    
    with patch('fastapi_app.app.routers.posts.get_blog_pages_count') as mock_count:
        mock_count.return_value = 3
        
        response = client.get("/api/posts/count")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        print("✅ Count endpoint test passed!")

if __name__ == "__main__":
    print("🧪 Running working FastAPI tests...")
    try:
        test_api_health()
        test_api_stats() 
        test_api_count()
        print("\n🎉 All working tests passed successfully!")
        print("📝 Note: Some tests require database setup and are excluded from this demo.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
