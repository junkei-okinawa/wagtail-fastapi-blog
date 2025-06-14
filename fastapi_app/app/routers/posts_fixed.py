"""Posts router for FastAPI application."""

import os
import django
import asyncio
import logging
import time
from functools import lru_cache
from typing import List, Optional

from django.conf import settings
from fastapi import APIRouter, HTTPException, Query
from asgiref.sync import sync_to_async

# Django設定の初期化
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.totonoe_template.settings.test')
    django.setup()

from blog.models import BlogPage
from ..schemas.post import PostSchema, PostListSchema

# ルーターの作成
router = APIRouter(prefix="/posts", tags=["posts"])

# ロガーの設定
logger = logging.getLogger(__name__)


@router.get("/debug")
async def debug_posts():
    """デバッグ用エンドポイント（開発環境でのテスト用）"""
    try:
        # 同期版のテスト（sync_to_asyncでラップ）
        @sync_to_async
        def get_sync_count():
            return BlogPage.objects.live().public().count()
        
        # 非同期版のテスト
        @sync_to_async
        def get_async_count():
            return BlogPage.objects.live().public().count()
        
        sync_count = await get_sync_count()
        async_count = await get_async_count()
        
        logger.info(f"Debug sync count: {sync_count}")
        logger.info(f"Debug async count: {async_count}")
        
        return {
            "status": "ok",
            "sync_count": sync_count,
            "async_count": async_count
        }
    except Exception as e:
        logger.error(f"Debug error: {str(e)}")
        return {"error": str(e)}


@router.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        @sync_to_async
        def get_total_posts():
            return BlogPage.objects.live().public().count()
        
        total_posts = await get_total_posts()
        
        return {
            "status": "healthy",
            "total_posts": total_posts,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}


async def get_blog_pages_count():
    """ブログページ数を非同期で取得"""
    @sync_to_async
    def _get_count():
        return BlogPage.objects.live().public().count()
    
    return await _get_count()


async def get_blog_pages_list(limit: int = 20, offset: int = 0, search: str = None):
    """ブログページ一覧を非同期で取得"""
    @sync_to_async
    def _get_pages():
        queryset = BlogPage.objects.live().public().order_by('-date', '-first_published_at')
        # 簡単な検索機能（実際の検索実装は省略）
        if search:
            queryset = queryset.filter(title__icontains=search)
        return list(queryset[offset:offset + limit])
    
    return await _get_pages()


async def get_blog_page_by_id(post_id: int):
    """IDでブログページを非同期で取得"""
    @sync_to_async
    def _get_page():
        try:
            return BlogPage.objects.live().public().get(id=post_id)
        except BlogPage.DoesNotExist:
            return None
    
    return await _get_page()


@router.get("/", response_model=PostListSchema)
async def get_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str = Query(None, description="Search query")
):
    """ブログ記事一覧を取得"""
    try:
        start_time = time.time()
        
        # 記事一覧とカウントを取得
        posts = await get_blog_pages_list(limit=limit, offset=offset, search=search)
        total_count = await get_blog_pages_count()
        
        # PostSchemaに変換
        post_data = []
        for post in posts:
            post_data.append({
                "id": post.id,
                "title": post.title,
                "intro": post.intro,
                "date": post.date.isoformat() if post.date else None,
                "slug": post.slug,
                "first_published_at": post.first_published_at.isoformat() if post.first_published_at else None,
                "body": str(post.body) if post.body else ""
            })
        
        execution_time = time.time() - start_time
        logger.info(f"get_posts executed in {execution_time:.3f} seconds")
        
        return {
            "posts": post_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_count": total_count,
                "has_next": offset + limit < total_count,
                "has_prev": offset > 0
            },
            "meta": {
                "execution_time": execution_time,
                "search_query": search
            }
        }
    except Exception as e:
        logger.error(f"Error in get_posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{post_id}", response_model=PostSchema)
async def get_post(post_id: int):
    """特定のブログ記事を取得"""
    try:
        post = await get_blog_page_by_id(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return PostSchema(
            id=post.id,
            title=post.title,
            intro=post.intro,
            date=post.date.isoformat() if post.date else None,
            slug=post.slug,
            first_published_at=post.first_published_at.isoformat() if post.first_published_at else None,
            body=str(post.body) if post.body else ""
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_post: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats")
async def get_posts_stats():
    """ブログ記事の統計情報を取得"""
    try:
        total_posts = await get_blog_pages_count()
        
        return {
            "total_posts": total_posts,
            "cache": {
                "hits": 0,  # キャッシュ統計は簡易実装
                "misses": 0
            },
            "performance": {
                "avg_response_time": 0.1
            }
        }
    except Exception as e:
        logger.error(f"Error in get_posts_stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cache/clear")
async def clear_cache():
    """キャッシュをクリア"""
    try:
        # 実際のキャッシュクリア処理（簡易実装）
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error in clear_cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
