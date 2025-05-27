from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from users_auth_app.models import UserProfileModel
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='business', password='pass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='pass')
        UserProfileModel.objects.create(
            user=self.customer_user, user_type='customer')

        offer = Offer.objects.create(
            user=self.business_user, title='Test Offer')

        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4.5,
            description='Sehr gut!'
        )

        self.url = reverse('base-info')

    def test_get_base_info_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)
