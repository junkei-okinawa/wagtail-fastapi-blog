"""Unit tests for FastAPI payments router."""

import pytest
from unittest.mock import patch, MagicMock
import responses
from fastapi import HTTPException

@pytest.mark.unit
class TestPaymentsRouter:
    """Test payments API router functionality."""
    
    def test_create_checkout_session_success(self, client, mock_stripe_key, sample_blog_data):
        """Test successful checkout session creation."""
        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/test"
        
        with patch('stripe.checkout.Session.create', return_value=mock_session):
            # レート制限をバイパス
            with patch('fastapi_app.app.routers.payments.rate_limit_check'):
                response = client.post("/api/payments/create-checkout-session", json=sample_blog_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["session_id"] == "cs_test_123"
                assert data["checkout_url"] == "https://checkout.stripe.com/test"
    
    def test_create_checkout_session_invalid_amount(self, client, mock_stripe_key):
        """Test checkout session creation with invalid amount."""
        invalid_data = {
            "article_id": 1,
            "amount": -100,  # Invalid negative amount
            "article_title": "Test Article",
            "success_url": "http://test.com/success/",
            "cancel_url": "http://test.com/cancel/"
        }
        
        response = client.post("/api/payments/create-checkout-session", json=invalid_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid amount" in data["detail"]
    
    def test_create_checkout_session_empty_title(self, client, mock_stripe_key):
        """Test checkout session creation with empty title."""
        invalid_data = {
            "article_id": 1,
            "amount": 500,
            "article_title": "",  # Empty title
            "success_url": "http://test.com/success/",
            "cancel_url": "http://test.com/cancel/"
        }
        
        response = client.post("/api/payments/create-checkout-session", json=invalid_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Article title is required" in data["detail"]
    
    def test_create_checkout_session_invalid_url(self, client, mock_stripe_key):
        """Test checkout session creation with invalid redirect URL."""
        invalid_data = {
            "article_id": 1,
            "amount": 500,
            "article_title": "Test Article",
            "success_url": "http://malicious-site.com/success/",  # Invalid domain
            "cancel_url": "http://test.com/cancel/"
        }
        
        response = client.post("/api/payments/create-checkout-session", json=invalid_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid redirect URL" in data["detail"]
    
    def test_create_checkout_session_stripe_error(self, client, mock_stripe_key, sample_blog_data):
        """Test checkout session creation when Stripe returns error."""
        import stripe
        
        with patch('stripe.checkout.Session.create', side_effect=stripe.error.StripeError("API Error")):
            response = client.post("/api/payments/create-checkout-session", json=sample_blog_data)
            
            assert response.status_code == 400
            data = response.json()
            assert "Payment processing error" in data["detail"]
    
    def test_rate_limiting(self, client, mock_stripe_key, sample_blog_data):
        """Test rate limiting functionality."""
        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/test"
        
        with patch('stripe.checkout.Session.create', return_value=mock_session):
            # Make multiple requests to trigger rate limiting
            for i in range(6):  # Rate limit is 5 requests per 60 seconds
                response = client.post("/api/payments/create-checkout-session", json=sample_blog_data)
                if i < 5:
                    assert response.status_code == 200
                else:
                    assert response.status_code == 429  # Rate limited
    
    def test_stripe_webhook_valid_signature(self, client, mock_stripe_key):
        """Test Stripe webhook with valid signature."""
        webhook_payload = '{"type": "checkout.session.completed", "data": {"object": {"id": "cs_123", "metadata": {"article_id": "1"}}}}'
        
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_event = {
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_123",
                        "metadata": {"article_id": "1"}
                    }
                }
            }
            mock_construct.return_value = mock_event
            
            response = client.post(
                "/api/payments/webhook",
                data=webhook_payload,
                headers={"stripe-signature": "test_signature"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_stripe_webhook_invalid_signature(self, client, mock_stripe_key):
        """Test Stripe webhook with invalid signature."""
        import stripe
        webhook_payload = '{"type": "test"}'
        
        with patch('stripe.Webhook.construct_event', side_effect=stripe.error.SignatureVerificationError("Invalid signature", "sig")):
            response = client.post(
                "/api/payments/webhook", 
                data=webhook_payload,
                headers={"stripe-signature": "invalid_signature"}
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Invalid signature" in data["detail"]


@pytest.mark.unit
class TestPaymentSchemas:
    """Test payment Pydantic schemas."""
    
    def test_checkout_session_request_validation(self):
        """Test CheckoutSessionRequest schema validation."""
        from fastapi_app.app.schemas.payment import CheckoutSessionRequest
        
        # Valid data
        valid_data = {
            "article_id": 1,
            "amount": 500,
            "article_title": "Test Article",
            "success_url": "http://test.com/success/",
            "cancel_url": "http://test.com/cancel/"
        }
        
        request = CheckoutSessionRequest(**valid_data)
        assert request.article_id == 1
        assert request.amount == 500
        assert request.article_title == "Test Article"
    
    def test_checkout_session_response_validation(self):
        """Test CheckoutSessionResponse schema validation."""
        from fastapi_app.app.schemas.payment import CheckoutSessionResponse
        
        valid_data = {
            "session_id": "cs_test_123",
            "checkout_url": "https://checkout.stripe.com/test"
        }
        
        response = CheckoutSessionResponse(**valid_data)
        assert response.session_id == "cs_test_123"
        assert response.checkout_url == "https://checkout.stripe.com/test"
