import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User

@pytest.mark.django_db
def test_register_sends_otp():
    client = APIClient()
    data = {
        'username': 'otpuser',
        'email': 'otp@example.com',
        'password': 'pass1234',
        'confirm_password': 'pass1234',
        'accept_terms': True
    }
    response = client.post(reverse('register'), data)
    assert response.status_code == 201
    user = User.objects.get(username='otpuser')
    assert user.email_otp is not None
    assert user.email_otp_expiry is not None

@pytest.mark.django_db
def test_password_reset_flow():
    user = User.objects.create_user(username='resetuser', email='reset@example.com', password='oldpass')
    client = APIClient()
    # request OTP
    response = client.post(reverse('password_reset_request'), {'email': user.email})
    assert response.status_code == 200
    user.refresh_from_db()
    otp = user.password_reset_otp
    assert otp is not None
    # confirm reset
    response = client.post(reverse('password_reset_confirm'), {
        'email': user.email,
        'otp': otp,
        'new_password': 'newpass123'
    })
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password('newpass123')
