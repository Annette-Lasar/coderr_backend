from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from users_auth_app.models import UserProfileModel

class UserAuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = UserProfileModel.objects.create(
            user=self.user,
            email='testuser@example.com',
            user_type='customer'
        )
        self.token_url = reverse('login')
        self.register_url = reverse('registration')
        self.profile_url = reverse('userprofile-detail', args=[self.user.id])

    def test_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'repeated_password': 'newpass123',
            'type': 'customer'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        data = {'username': 'testuser', 'password': 'testpass'}
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_profile(self):
        self.client.force_authenticate(user=self.user)
        data = {'description': 'Updated description'}
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.description, 'Updated description')

    def test_get_business_users(self):
        url = reverse('business-user-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_customer_users(self):
        url = reverse('customer-user-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

