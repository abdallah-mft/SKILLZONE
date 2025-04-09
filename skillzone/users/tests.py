import pytest
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.mark.django_db
class TestUserAPI:
    def test_user_registration(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123',  # Updated with uppercase
            'password2': 'NewPass123',  # Updated with uppercase
            'first_name': 'New',
            'last_name': 'User',
            'accept_terms': True
        }
        response = api_client.post(url, data, format='json')
        if response.status_code != 201:
            print("Registration failed with:", response.content)
        assert response.status_code == 201

    def test_user_login(self, api_client, test_user):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == 200

    def test_password_reset_request(self, api_client, test_user):
        url = reverse('password-reset')  # Updated URL name
        data = {'email': test_user.email}
        response = api_client.post(url, data)
        assert response.status_code == 200

    def test_email_verification(self, api_client, test_user):
        url = reverse('verify-email', kwargs={'token': 'test-token'})
        response = api_client.get(url)
        assert response.status_code in [200, 400]  # Either success or invalid token

@pytest.mark.django_db
class TestSecurityHeaders:
    def test_security_headers(self, api_client):
        response = api_client.get(reverse('users_index'))
        assert response.status_code == 200
        assert 'X-Frame-Options' in response.headers

@pytest.mark.django_db
class TestEmailTemplates:
    def test_verification_email_content(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123',  # Updated with uppercase
            'password2': 'NewPass123'  # Updated with uppercase
        }
        response = api_client.post(url, data)
        assert response.status_code == 201
        assert len(mail.outbox) > 0

    def test_password_reset_email_content(self, api_client, test_user):
        url = reverse('password-reset')  # Updated URL name
        data = {'email': test_user.email}
        response = api_client.post(url, data)
        assert response.status_code == 200
        assert len(mail.outbox) > 0
