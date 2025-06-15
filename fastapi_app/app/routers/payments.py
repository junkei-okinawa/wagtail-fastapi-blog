import logging
import os
import time
from collections import defaultdict

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request

from ..schemas.payment import CheckoutSessionRequest, CheckoutSessionResponse

# 環境変数を読み込み
load_dotenv()

# ログ設定
logger = logging.getLogger(__name__)

# Stripe API キーを設定
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(prefix="/payments", tags=["payments"])


# CORS Preflight endpoints
@router.options("/health")
async def health_check_options():
    """Handle CORS preflight for payment health endpoint."""
    return {"message": "CORS preflight handled"}


@router.options("/create-checkout-session")
async def create_checkout_session_options():
    """Handle CORS preflight for checkout session endpoint."""
    return {"message": "CORS preflight handled"}


# レート制限用の簡単な実装（本番では Redis 等を使用）
request_counts = defaultdict(list)


def rate_limit_check(
    request: Request, max_requests: int = 10, window_seconds: int = 60
):
    """簡単なレート制限チェック"""
    client_ip = request.client.host
    now = time.time()

    # 古いリクエストを削除
    request_counts[client_ip] = [
        timestamp
        for timestamp in request_counts[client_ip]
        if now - timestamp < window_seconds
    ]

    # リクエスト数をチェック
    if len(request_counts[client_ip]) >= max_requests:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # 新しいリクエストを記録
    request_counts[client_ip].append(now)


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request_data: CheckoutSessionRequest, request: Request
):
    """Stripe Checkout セッションを作成"""

    # レート制限チェック
    try:
        rate_limit_check(request, max_requests=5, window_seconds=60)
    except HTTPException:
        raise

    # 入力検証
    if request_data.amount <= 0 or request_data.amount > 100000:  # 0円〜10万円の範囲
        raise HTTPException(status_code=400, detail="Invalid amount")

    if not request_data.article_title.strip():
        raise HTTPException(status_code=400, detail="Article title is required")

    # URLの検証
    allowed_domains = ["localhost", "127.0.0.1", "yourdomain.com"]  # 許可するドメイン
    for url in [request_data.success_url, request_data.cancel_url]:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.hostname not in allowed_domains:
            raise HTTPException(status_code=400, detail="Invalid redirect URL")

    try:
        # Stripe Checkout セッションを作成
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "jpy",
                        "product_data": {
                            "name": request_data.article_title[:100],  # 長さ制限
                            "description": f"記事ID: {request_data.article_id} の購入",
                        },
                        "unit_amount": request_data.amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request_data.success_url,
            cancel_url=request_data.cancel_url,
            metadata={
                "article_id": str(request_data.article_id),
                "client_ip": request.client.host,
            },
            expires_at=int(time.time()) + 1800,  # 30分で期限切れ
        )

        logger.info(
            f"Checkout session created: {session.id} "
            f"for article {request_data.article_id}"
        )

        return CheckoutSessionResponse(session_id=session.id, checkout_url=session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e!s}")
        raise HTTPException(status_code=400, detail="Payment processing error")
    except Exception as e:
        logger.error(f"Internal error in create_checkout_session: {e!s}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Stripe Webhook エンドポイント"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if not webhook_secret:
            logger.error("Webhook secret not configured")
            raise HTTPException(status_code=500, detail="Configuration error")

        # Webhook イベントを検証
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError as e:
            logger.warning(f"Invalid payload: {e!s}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.warning(f"Invalid signature: {e!s}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # イベントタイプに応じて処理
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            article_id = session.get("metadata", {}).get("article_id")

            # TODO: ここで購入完了処理を実装
            # - データベースに購入記録を保存
            # - ユーザーに購入完了メールを送信
            # - 記事へのアクセス権限を付与

            logger.info(f"購入完了: 記事ID {article_id}, セッションID {session['id']}")

        elif event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            article_id = payment_intent.get("metadata", {}).get("article_id")

            logger.info(
                f"決済成功: 記事ID {article_id}, Payment Intent ID {payment_intent['id']}"
            )

        return {"status": "success"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook エラー: {e!s}")
        raise HTTPException(status_code=500, detail="Webhook processing error")


@router.get("/test")
async def test_stripe_connection():
    """Stripe 接続テスト用エンドポイント（開発環境のみ）"""
    if os.getenv("DEBUG", "False").lower() != "true":
        raise HTTPException(status_code=404, detail="Not found")

    try:
        # アカウント情報を取得してテスト
        account = stripe.Account.retrieve()
        return {
            "status": "success",
            "account_id": account.id,
            "country": account.country,
            "message": "Stripe connection successful",
        }
    except stripe.error.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid Stripe API key")
    except Exception as e:
        logger.error(f"Stripe connection error: {e!s}")
        raise HTTPException(status_code=500, detail="Stripe connection error")
