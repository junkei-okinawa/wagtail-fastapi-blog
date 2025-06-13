import os
import django
from django.conf import settings
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from asgiref.sync import sync_to_async
from functools import lru_cache
import asyncio
import logging
import time

# Django 設定の初期化
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.totonoe_template.settings.dev")
django.setup()

from blog.models import BlogPage
from ..schemas.post import PostSchema, PostListSchema

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/posts", tags=["posts"])

# キャッシュ用のデコレータ
@lru_cache(maxsize=128)
def _get_cached_blog_pages(limit: int = 20, offset: int = 0):
    """ブログ記事一覧をキャッシュ付きで取得（同期関数）"""
    start_time = time.time()
    try:
        result = list(
            BlogPage.objects
            .live()
            .public()
            .order_by('-date', '-first_published_at')
            [offset:offset + limit]
        )
        execution_time = time.time() - start_time
        logger.info(f"_get_cached_blog_pages executed in {execution_time:.3f} seconds, returned {len(result)} posts")
        return result
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"_get_cached_blog_pages failed after {execution_time:.3f} seconds: {str(e)}")
        raise

@sync_to_async
def get_blog_pages_optimized(limit: int = 20, offset: int = 0):
    """最適化されたブログ記事一覧取得"""
    return _get_cached_blog_pages(limit, offset)

@sync_to_async
def get_blog_page_by_id_optimized(page_id: int):
    """IDでブログ記事を最適化して取得（同期関数）"""
    try:
        return BlogPage.objects.live().public().get(id=page_id)
    except BlogPage.DoesNotExist:
        return None

@sync_to_async
def get_blog_pages_count():
    """ブログ記事の総数を取得"""
    return BlogPage.objects.live().public().count()

@router.get("/", response_model=dict)
async def list_posts(
    limit: int = Query(default=20, le=100, ge=1, description="取得件数（最大100件）"),
    offset: int = Query(default=0, ge=0, description="オフセット"),
    page: int = Query(default=1, ge=1, description="ページ番号"),
    search: Optional[str] = Query(default=None, description="検索キーワード")
):
    """
    ブログ記事一覧を取得する最適化された API エンドポイント
    
    - ページネーション対応
    - 検索機能付き
    - キャッシュ機能付き
    - パフォーマンス監視付き
    """
    start_time = time.time()
    
    try:
        # pageパラメータからoffsetを計算（pageが指定されている場合）
        if page > 1:
            offset = (page - 1) * limit
        
        # 同期関数として実装し、sync_to_asyncで実行
        @sync_to_async
        def get_posts_data():
            try:
                # 総数を取得
                total_count = BlogPage.objects.live().public().count()
                
                # 記事一覧を取得（シンプルな最適化のみ）
                posts = (BlogPage.objects
                        .live()
                        .public()
                        .order_by('-date', '-first_published_at')
                        [offset:offset + limit])
                
                post_list = []
                for post in posts:
                    post_list.append({
                        "id": post.id,
                        "title": post.title,
                        "intro": post.intro,
                        "date": str(post.date) if post.date else None,
                        "slug": post.slug,
                        "url_path": post.url_path
                    })
                
                return total_count, post_list
            except Exception as e:
                logger.error(f"Error in get_posts_data: {str(e)}")
                raise
        
        total_count, posts = await get_posts_data()
        
        # ページネーション情報を計算
        total_pages = (total_count + limit - 1) // limit
        has_next = offset + limit < total_count
        has_prev = offset > 0
        current_page = (offset // limit) + 1
        
        response_data = {
            "posts": posts,
            "pagination": {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": current_page,
                "per_page": limit,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": current_page + 1 if has_next else None,
                "prev_page": current_page - 1 if has_prev else None,
            },
            "meta": {
                "search_query": search,
                "execution_time": round(time.time() - start_time, 3)
            }
        }
        
        total_time = time.time() - start_time
        logger.info(f"list_posts completed in {total_time:.3f} seconds")
        return response_data
        
    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"list_posts failed after {error_time:.3f} seconds: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/count")
async def get_posts_count():
    """ブログ記事の総数を取得（ページネーション用）"""
    count = await get_blog_pages_count()
    return {"count": count}

# パフォーマンス統計エンドポイント（{post_id}より前に配置）
@router.get("/stats")
async def get_performance_stats():
    """パフォーマンス統計情報を取得"""
    try:
        cache_info = _get_cached_blog_pages.cache_info()
        return {
            "cache": {
                "hits": cache_info.hits,
                "misses": cache_info.misses,
                "current_size": cache_info.currsize,
                "max_size": cache_info.maxsize,
                "hit_rate": cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0
            },
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Failed to get performance stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance stats")

# ヘルスチェックエンドポイント（{post_id}より前に配置）
@router.get("/health")
async def health_check():
    """API ヘルスチェック"""
    start_time = time.time()
    try:
        # 簡単なDB接続テスト
        count = await get_blog_pages_count()
        execution_time = time.time() - start_time
        return {
            "status": "healthy",
            "total_posts": count,
            "execution_time": round(execution_time, 3),
            "timestamp": time.time()
        }
    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"Health check failed after {error_time:.3f} seconds: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# デバッグ用エンドポイント（{post_id}より前に配置）
@router.get("/debug")
async def debug_posts():
    """デバッグ用エンドポイント"""
    try:
        # 同期関数でのテスト
        count = BlogPage.objects.live().public().count()
        logger.info(f"Debug count: {count}")
        
        # 非同期版のテスト
        async_count = await get_blog_pages_count()
        logger.info(f"Debug async count: {async_count}")
        
        return {
            "status": "ok",
            "sync_count": count,
            "async_count": async_count
        }
    except Exception as e:
        logger.error(f"Debug error: {str(e)}")
        return {"error": str(e)}

# シンプルなテスト用エンドポイント
@router.get("/simple")
async def simple_posts():
    """シンプルなテスト用記事一覧"""
    try:
        # sync_to_asyncを使用して同期関数を非同期で実行
        @sync_to_async
        def get_simple_posts():
            posts = BlogPage.objects.live().public()[:5]
            result = []
            for post in posts:
                result.append({
                    "id": post.id,
                    "title": post.title,
                    "date": str(post.date) if post.date else None
                })
            return result
        
        posts = await get_simple_posts()
        return {"posts": posts, "count": len(posts)}
    except Exception as e:
        logger.error(f"Simple posts error: {str(e)}")
        return {"error": str(e), "type": type(e).__name__}

# キャッシュ付きエンドポイント
@router.get("/cached")
async def cached_posts(
    limit: int = Query(default=5, le=20, ge=1, description="取得件数"),
    offset: int = Query(default=0, ge=0, description="オフセット")
):
    """キャッシュ機能付きの記事一覧"""
    try:
        posts = await get_blog_pages_optimized(limit, offset)
        result = []
        for post in posts:
            result.append({
                "id": post.id,
                "title": post.title,
                "date": str(post.date) if post.date else None,
                "slug": post.slug
            })
        return {"posts": result, "count": len(result), "cached": True}
    except Exception as e:
        logger.error(f"Cached posts error: {str(e)}")
        return {"error": str(e), "type": type(e).__name__}

@router.get("/{post_id}", response_model=PostSchema)
async def get_post(post_id: int):
    """IDでブログ記事詳細を最適化して取得する API エンドポイント"""
    post = await get_blog_page_by_id_optimized(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return PostSchema(
        id=post.id,
        title=post.title,
        intro=post.intro,
        date=post.date,
        slug=post.slug,
        body=post.body,  # RichTextField の内容
        url_path=post.url_path
    )

# キャッシュクリア用エンドポイント（管理用）
@router.post("/cache/clear")
async def clear_cache():
    """キャッシュをクリア（開発・管理用）"""
    start_time = time.time()
    try:
        _get_cached_blog_pages.cache_clear()
        execution_time = time.time() - start_time
        logger.info(f"Cache cleared in {execution_time:.3f} seconds")
        return {"message": "Cache cleared successfully", "execution_time": round(execution_time, 3)}
    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"Cache clear failed after {error_time:.3f} seconds: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")
