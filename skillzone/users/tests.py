import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestUserAPI:
    def setup_method(self):
        self.register_url = reverse('user-register')
        self.login_url = reverse('user-login')
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'accept_terms': True
        }

    def test_full_user_journey(self, client):
        response = client.post(self.register_url, self.test_user_data)
        assert response.status_code == status.HTTP_201_CREATED

        login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = client.post(self.login_url, login_data)
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_login(self, client):
        login_data = {
            'username': 'nonexistent',
            'password': 'wrong'
        }
        response = client.post(self.login_url, login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_registration(self, client):
        invalid_data = self.test_user_data.copy()
        invalid_data['password2'] = 'different'
        response = client.post(self.register_url, invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthorized_access(self, client):
        protected_url = reverse('user-profile')
        response = client.get(protected_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestEmailVerification:
    def test_email_verification_flow(self, client):
        # Register a new user
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'accept_terms': True
        }
        response = client.post(reverse('user-register'), user_data)
        assert response.status_code == status.HTTP_201_CREATED

        # Get the verification code
        user = User.objects.get(username='testuser')
        verification_code = user.profile.verification_code

        # Test invalid code
        response = client.post(reverse('verify-email'), {
            'email': 'test@example.com',
            'code': 'WRONG'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test valid code
        response = client.post(reverse('verify-email'), {
            'email': 'test@example.com',
            'code': verification_code
        })
        assert response.status_code == status.HTTP_200_OK

        # Verify that email is marked as verified
        user.refresh_from_db()
        assert user.profile.email_verified == True

        # Test attempting to verify again
        response = client.post(reverse('verify-email'), {
            'email': 'test@example.com',
            'code': verification_code
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already verified' in response.json()['message']
