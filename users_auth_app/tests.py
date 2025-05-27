from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from users_auth_app.models import UserProfileModel


class UserAuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
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

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profile/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_profile(self):
        self.client.force_authenticate(user=self.user)
        data = {'description': 'Updated description'}
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.description, 'Updated description')

    def test_update_profile_user_fields(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'email': 'new_email@example.com'
        }
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Max')
        self.assertEqual(self.user.last_name, 'Mustermann')
        self.assertEqual(self.user.email, 'new_email@example.com')

    def test_update_profile_response_body(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'description': 'Updated description',
            'working_hours': '10-18',
            'email': 'new_email@example.com'
        }
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_keys = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type', 'email', 'created_at'
        ]
        for key in expected_keys:
            self.assertIn(key, response.data)

        self.assertEqual(response.data['first_name'], 'Max')
        self.assertEqual(response.data['last_name'], 'Mustermann')
        self.assertEqual(response.data['description'], 'Updated description')
        self.assertEqual(response.data['working_hours'], '10-18')
        self.assertEqual(response.data['email'], 'new_email@example.com')

    def test_business_user_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if response.data:
            user_entry = response.data[0]
            self.assertIn('user', user_entry)
            self.assertIn('username', user_entry['user'])
            self.assertIn('first_name', user_entry['user'])
            self.assertIn('last_name', user_entry['user'])
            self.assertIn('file', user_entry)
            self.assertIn('location', user_entry)
            self.assertIn('tel', user_entry)
            self.assertIn('description', user_entry)
            self.assertIn('working_hours', user_entry)
            self.assertIn('type', user_entry)

    def test_business_user_list_unauthenticated(self):
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_customer_users(self):
        url = reverse('customer-user-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if response.data:
            user_entry = response.data[0]
            self.assertIn('user', user_entry)
            self.assertIn('file', user_entry)
            self.assertIn('uploaded_at', user_entry)
            self.assertIn('type', user_entry)
            self.assertIn('username', user_entry['user'])
            self.assertIn('first_name', user_entry['user'])
            self.assertIn('last_name', user_entry['user'])

    def test_get_customer_users_unauthenticated(self):
        url = reverse('customer-user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_customer_users_returned(self):
        url = reverse('customer-user-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        for user_entry in response.data:
            self.assertEqual(user_entry['type'], 'customer')
