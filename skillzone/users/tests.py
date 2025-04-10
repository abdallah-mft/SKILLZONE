from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Profile
import json

User = get_user_model()

class TestUserAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = '/api/v1/users'  # Add base URL
        self.register_data = {
            "email": "zayd.benali@example.com",
            "username": "zaydben",
            "password": "ZaydStrong123",
            "password2": "ZaydStrong123",
            "first_name": "Zayd",
            "last_name": "Benali",
            "accept_terms": True
        }
        self.login_data = {
            "email": "zayd.benali@example.com",
            "password": "ZaydStrong123"
        }
        self.profile_update_data = {
            "first_name": "Zayd",
            "last_name": "Benali",
            "bio": "Cybersecurity Enthusiast & Tech Explorer 🚀",
            "notification_preferences": {
                "email_notifications": True,
                "push_notifications": False
            }
        }

    def test_full_user_journey(self):
        # 1. Test Registration
        register_response = self.client.post(
            f'{self.base_url}/register/',
            self.register_data,
            format='json'
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(register_response.data['success'])
        self.assertIn('access', register_response.data['data'])

        # 2. Test Login
        login_response = self.client.post(
            f'{self.base_url}/login/',
            self.login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertTrue(login_response.data['success'])
        access_token = login_response.data['data']['access']

        # Set token for authenticated requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 3. Test Get Profile
        profile_response = self.client.get(f'{self.base_url}/profile/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        # Verify profile data exists instead of checking 'success' key
        self.assertIn('user', profile_response.data)

        # 4. Test Profile Update
        update_response = self.client.put(
            f'{self.base_url}/profile/update/',
            self.profile_update_data,
            format='json'
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertTrue(update_response.data['success'])

        # 5. Test Password Change
        password_response = self.client.post(
            f'{self.base_url}/profile/change-password/',
            {
                'current_password': 'ZaydStrong123',
                'new_password': 'ZaydNewPass456'
            },
            format='json'
        )
        self.assertEqual(password_response.status_code, status.HTTP_200_OK)
        self.assertTrue(password_response.data['success'])

        # Verify can login with new password
        new_login_response = self.client.post(
            f'{self.base_url}/login/',
            {
                "email": "zayd.benali@example.com",
                "password": "ZaydNewPass456"
            },
            format='json'
        )
        self.assertEqual(new_login_response.status_code, status.HTTP_200_OK)
        self.assertTrue(new_login_response.data['success'])

    def test_invalid_registration(self):
        invalid_data = self.register_data.copy()
        invalid_data.pop('email')
        response = self.client.post(
            f'{self.base_url}/register/',
            invalid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_invalid_login(self):
        # First register a user
        self.client.post(
            f'{self.base_url}/register/',
            self.register_data,
            format='json'
        )
        
        # Then try to login with wrong password
        invalid_login = self.login_data.copy()
        invalid_login['password'] = 'wrongpassword'
        response = self.client.post(
            f'{self.base_url}/login/',
            invalid_login,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])

    def test_unauthorized_access(self):
        response = self.client.get(f'{self.base_url}/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
