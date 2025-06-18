import pytest
from unittest.mock import MagicMock
from accounts.models import User, Subscription
from accounts.services.stripe_service import create_subscription

@pytest.mark.django_db
def test_create_subscription(monkeypatch):
    user = User.objects.create_user(username="u", password="pass")

    fake_sub = MagicMock(id="sub_123", status="active")
    monkeypatch.setattr('accounts.services.stripe_service.create_stripe_customer', lambda u: 'cus_123')
    monkeypatch.setattr('stripe.Subscription.create', lambda **kwargs: fake_sub)

    sub_id = create_subscription(user, 'price_123')

    assert sub_id == "sub_123"
    sub = Subscription.objects.get(user=user)
    assert sub.stripe_subscription_id == "sub_123"
    assert sub.status == "active"
