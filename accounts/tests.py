import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from .models import User

@pytest.mark.django_db
def test_user_retrieve():
    client = APIClient()
    user = User.objects.create_user(
        username='testuser', password='testpass', email='test@example.com',
        is_buyer=True, is_seller=True, is_verifier=False
    )
    client.force_authenticate(user=user)
    response = client.get(reverse('user-list'))
    assert response.status_code == 200
    assert response.data[0]['username'] == 'testuser'
    assert response.data[0]['is_buyer'] is True
    assert response.data[0]['is_seller'] is True
    assert response.data[0]['is_verifier'] is False

@pytest.mark.django_db
def test_user_unauthenticated():
    client = APIClient()
    response = client.get(reverse('user-list'))
    assert response.status_code == 401

@pytest.mark.django_db
def test_register_user():
    client = APIClient()
    response = client.post(
        reverse('register'),
        {'username': 'newuser', 'email': 'newuser@example.com', 'password': 'newpass'}
    )
    assert response.status_code == 201
    assert User.objects.filter(username='newuser').exists()
    user = User.objects.get(username='newuser')
    assert user.is_buyer is True
    assert user.is_seller is True
    assert user.is_verifier is False

@pytest.mark.django_db
def test_change_role_admin():
    client = APIClient()
    admin = User.objects.create_superuser(
        username='admin', password='adminpass', email='admin@example.com'
    )
    user = User.objects.create_user(
        username='testuser', password='testpass', email='test@example.com',
        is_buyer=True, is_seller=True, is_verifier=False
    )
    client.force_authenticate(user=admin)
    response = client.patch(
        reverse('change-role', kwargs={'user_id': user.id}),
        {'is_verifier': True}
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_verifier is True