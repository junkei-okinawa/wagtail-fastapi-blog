from typing import Optional

from pydantic import BaseModel


class PaymentIntentRequest(BaseModel):
    """決済インテント作成リクエスト"""

    article_id: int
    amount: int  # 金額（円）
    currency: str = "jpy"


class PaymentIntentResponse(BaseModel):
    """決済インテント作成レスポンス"""

    client_secret: str
    payment_intent_id: str
    amount: int
    currency: str


class CheckoutSessionRequest(BaseModel):
    """Stripe Checkout セッション作成リクエスト"""

    article_id: int
    amount: int  # 金額（円）
    article_title: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Stripe Checkout セッション作成レスポンス"""

    session_id: str
    checkout_url: str


class WebhookEvent(BaseModel):
    """Stripe Webhook イベント"""

    event_type: str
    payment_intent_id: Optional[str] = None
    session_id: Optional[str] = None
    status: str
    amount: Optional[int] = None
