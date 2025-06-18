import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from accounts.models import User
from orders.models import Order
from .models import Dispute


@pytest.mark.django_db
def test_create_dispute():
    client = APIClient()
    user = User.objects.create_user(username="buyer", password="pass")
    order = Order.objects.create(
        buyer=user,
        base_price=10,
        buyer_processing_fee=1,
        buyer_shipping_fee=1,
        buyer_total_price=12,
    )
    client.force_authenticate(user=user)
    url = reverse("dispute-list")
    response = client.post(url, {"order_id": order.id})
    assert response.status_code == 201
    assert response.data["status"] == "open"


@pytest.mark.django_db
def test_add_message():
    user = User.objects.create_user(username="buyer", password="pass")
    order = Order.objects.create(
        buyer=user,
        base_price=10,
        buyer_processing_fee=1,
        buyer_shipping_fee=1,
        buyer_total_price=12,
    )
    dispute = Dispute.objects.create(order=order, initiator=user)
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("dispute-add-message", args=[dispute.id])
    response = client.post(url, {"content": "hello"})
    assert response.status_code == 201
    dispute.refresh_from_db()
    assert dispute.messages.count() == 1


@pytest.mark.django_db
def test_resolve_dispute():
    user = User.objects.create_user(username="buyer", password="pass")
    order = Order.objects.create(
        buyer=user,
        base_price=10,
        buyer_processing_fee=1,
        buyer_shipping_fee=1,
        buyer_total_price=12,
    )
    dispute = Dispute.objects.create(order=order, initiator=user)
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("dispute-resolve", args=[dispute.id])
    response = client.post(url)
    assert response.status_code == 200
    dispute.refresh_from_db()
    assert dispute.status == "resolved"


@pytest.mark.django_db
def test_access_rights():
    buyer = User.objects.create_user(username="buyer", password="pass")
    other = User.objects.create_user(username="other", password="pass")
    order = Order.objects.create(
        buyer=buyer,
        base_price=10,
        buyer_processing_fee=1,
        buyer_shipping_fee=1,
        buyer_total_price=12,
    )
    dispute = Dispute.objects.create(order=order, initiator=buyer)
    client = APIClient()
    client.force_authenticate(user=other)
    url = reverse("dispute-add-message", args=[dispute.id])
    assert client.post(url, {"content": "test"}).status_code == 403
    url = reverse("dispute-resolve", args=[dispute.id])
    assert client.post(url).status_code == 403
    # opening dispute on order of another user
    url = reverse("dispute-list")
    resp = client.post(url, {"order_id": order.id})
    assert resp.status_code == 400
