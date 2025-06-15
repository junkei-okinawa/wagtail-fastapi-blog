"""
FastAPI アプリケーションのパフォーマンス最適化ユーティリティ
"""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


class AsyncCache:
    """非同期キャッシュクラス"""

    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl

    async def get(self, key: str) -> Any:
        """キャッシュから値を取得"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    async def set(self, key: str, value: Any):
        """キャッシュに値を設定"""
        self.cache[key] = (value, time.time())

    async def clear(self):
        """キャッシュをクリア"""
        self.cache.clear()

    async def delete(self, key: str):
        """特定のキーを削除"""
        if key in self.cache:
            del self.cache[key]


# グローバルキャッシュインスタンス
async_cache = AsyncCache(ttl=300)  # 5分間のキャッシュ


def async_cached(ttl: int = 300):
    """非同期関数用のキャッシュデコレータ"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # キャッシュキーを生成
            key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # キャッシュから取得を試行
            cached_result = await async_cache.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # キャッシュミスの場合は関数を実行
            logger.debug(f"Cache miss for {func.__name__}")
            result = await func(*args, **kwargs)

            # 結果をキャッシュに保存
            await async_cache.set(key, result)
            return result

        wrapper.cache_clear = async_cache.clear
        wrapper.cache_delete = async_cache.delete
        return wrapper

    return decorator


def rate_limit(calls: int, period: int):
    """レート制限デコレータ"""
    call_times = []

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            # 期間外の呼び出しを削除
            while call_times and call_times[0] <= now - period:
                call_times.pop(0)

            # レート制限チェック
            if len(call_times) >= calls:
                raise Exception(
                    f"Rate limit exceeded: {calls} calls per {period} seconds"
                )

            call_times.append(now)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class DatabaseOptimizer:
    """データベースクエリ最適化ユーティリティ"""

    @staticmethod
    def optimize_queryset(
        queryset,
        select_related_fields=None,
        prefetch_related_fields=None,
        only_fields=None,
    ):
        """クエリセットを最適化"""
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)

        if prefetch_related_fields:
            queryset = queryset.prefetch_related(*prefetch_related_fields)

        if only_fields:
            queryset = queryset.only(*only_fields)

        return queryset

    @staticmethod
    def get_pagination_info(total_count: int, page: int, per_page: int):
        """ページネーション情報を計算"""
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1

        return {
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": page + 1 if has_next else None,
            "prev_page": page - 1 if has_prev else None,
        }


# Performance monitoring
class PerformanceMonitor:
    """パフォーマンス監視クラス"""

    @staticmethod
    def time_async_function(func: Callable) -> Callable:
        """非同期関数の実行時間を測定するデコレータ"""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} executed in {execution_time:.3f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed after {execution_time:.3f} seconds: {e!s}"
                )
                raise

        return wrapper
