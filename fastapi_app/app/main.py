from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request
import os
from .routers import posts, payments  # payments ルーターを追加

# FastAPI アプリケーションのインスタンス作成
app = FastAPI(
    title="totonoe_template API",
    description="Django (Wagtail) + FastAPI ブログサイトの API",
    version="0.1.0",
    docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,  # 本番環境では無効化
    redoc_url="/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None,  # 本番環境では無効化
)

# セキュリティミドルウェア: 信頼できるホストのみ許可
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]  # 本番ドメインを追加
)

# CORS設定（より厳密に）
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # 必要なメソッドのみ許可
    allow_headers=["Content-Type", "Authorization"],  # 必要なヘッダーのみ許可
)

# グローバルエラーハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 本番環境では詳細なエラーメッセージを隠す
    if os.getenv("DEBUG", "False").lower() == "true":
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# ルーターの登録
app.include_router(posts.router)
app.include_router(payments.router)  # 決済ルーターを追加

@app.get("/")
async def root():
    """API のルートエンドポイント"""
    return {
        "message": "totonoe_template FastAPI",
        "version": "0.1.0",
        "docs": "/docs" if os.getenv("DEBUG", "False").lower() == "true" else "disabled",
        "endpoints": {
            "posts": "/posts",
            "payments": "/payments"
        }
    }
