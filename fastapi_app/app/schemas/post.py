from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    """ブログ記事の基本スキーマ"""

    id: int
    title: str
    intro: str
    date: str | None = None  # ISO format string
    slug: str
    first_published_at: str | None = None  # ISO format string
    body: str


class PostSchema(PostBase):
    """ブログ記事の詳細スキーマ（API レスポンス用）"""

    model_config = ConfigDict(from_attributes=True)


class PostListItemSchema(BaseModel):
    """ブログ記事一覧の個別アイテム用スキーマ"""

    id: int
    title: str
    intro: str
    date: str | None = None  # ISO format string
    slug: str
    first_published_at: str | None = None  # ISO format string
    body: str

    model_config = ConfigDict(from_attributes=True)


class PaginationSchema(BaseModel):
    """ページネーション情報スキーマ"""

    limit: int
    offset: int
    total_count: int
    has_next: bool
    has_prev: bool


class MetaSchema(BaseModel):
    """メタ情報スキーマ"""

    execution_time: float
    search_query: str | None = None


class PostListSchema(BaseModel):
    """ブログ記事一覧レスポンス用スキーマ"""

    posts: list[PostListItemSchema]
    pagination: PaginationSchema
    meta: MetaSchema

    model_config = ConfigDict(from_attributes=True)


class CacheStatsSchema(BaseModel):
    """キャッシュ統計スキーマ"""

    hits: int
    misses: int


class PerformanceStatsSchema(BaseModel):
    """パフォーマンス統計スキーマ"""

    avg_response_time: float


class PostStatsSchema(BaseModel):
    """投稿統計情報スキーマ"""

    total_posts: int
    cache: CacheStatsSchema
    performance: PerformanceStatsSchema


class CacheClearSchema(BaseModel):
    """キャッシュクリア結果スキーマ"""

    message: str
