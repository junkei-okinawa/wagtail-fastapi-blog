from datetime import date
from typing import Optional
from pydantic import BaseModel


class PostBase(BaseModel):
    """ブログ記事の基本スキーマ"""
    title: str
    intro: str
    date: date


class PostSchema(PostBase):
    """ブログ記事の詳細スキーマ（API レスポンス用）"""
    id: int
    slug: str
    body: str
    url_path: str
    
    class Config:
        from_attributes = True


class PostListSchema(PostBase):
    """ブログ記事一覧用スキーマ（簡略版）"""
    id: int
    slug: str
    url_path: str
    
    class Config:
        from_attributes = True
