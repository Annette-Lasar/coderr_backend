from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from users_auth_app.models import UserProfileModel
from reviews_app.models import Review


class ReviewListTests(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            username='customer', password='testpass')
        UserProfileModel.objects.create(
            user=self.customer_user, user_type='customer')

        self.business_user1 = User.objects.create_user(
            username='business1', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user1, user_type='business')

        self.business_user2 = User.objects.create_user(
            username='business2', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user2, user_type='business')

        self.review1 = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.customer_user,
            rating=4,
            description='Sehr professioneller Service.'
        )
        self.review2 = Review.objects.create(
            business_user=self.business_user2,
            reviewer=self.customer_user,
            rating=5,
            description='Top Qualität und schnelle Lieferung!'
        )

        self.url = reverse('reviews-list')

    def test_get_reviews_authenticated(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 2)

    def test_get_reviews_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_reviews_by_business_user(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(
            self.url, {'business_user_id': self.business_user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for review in response.data:
            self.assertEqual(review['business_user'], self.business_user1.id)

    def test_order_reviews_by_rating(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url, {'ordering': '-rating'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [review['rating'] for review in response.data]
        self.assertEqual(ratings, sorted(ratings, reverse=True))


class ReviewCreationTests(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            username='customeruser', password='testpass')
        UserProfileModel.objects.create(
            user=self.customer_user, user_type='customer')

        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.url = reverse('reviews-list')

    def test_create_review_success(self):
        self.client.force_authenticate(user=self.customer_user)
        data = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': 'Sehr guter Service!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['reviewer'], self.customer_user.id)

    def test_create_duplicate_review_forbidden(self):
        # Erste Bewertung anlegen
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description='Erste Bewertung'
        )

        self.client.force_authenticate(user=self.customer_user)
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Zweite Bewertung'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Du hast bereits eine Bewertung', str(response.data))

    def test_create_review_unauthenticated(self):
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Test ohne Login'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewUpdateTests(APITestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user(
            username='reviewer', password='testpass')
        self.business_user = User.objects.create_user(
            username='business', password='testpass')

        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Sehr gut!'
        )

        self.url = reverse('reviews-detail', args=[self.review.id])

    def test_reviewer_can_update_review(self):
        self.client.force_authenticate(user=self.reviewer)
        data = {'rating': 5, 'description': 'Noch besser als erwartet!'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(
            response.data['description'], 'Noch besser als erwartet!')

    def test_non_reviewer_cannot_update_review(self):
        other_user = User.objects.create_user(
            username='other', password='testpass')
        self.client.force_authenticate(user=other_user)
        data = {'rating': 5, 'description': 'Ich greife hier unrechtmäßig ein.'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_update_review(self):
        data = {'rating': 5, 'description': 'Ich bin nicht eingeloggt.'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_with_invalid_data(self):
        self.client.force_authenticate(user=self.reviewer)
        data = {'rating': 'ungültig'}  # Rating soll eine Zahl sein!
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_review(self):
        self.client.force_authenticate(user=self.reviewer)
        nonexistent_url = reverse('reviews-detail', args=[999999])
        data = {'rating': 5, 'description': 'Test auf nicht existente ID'}
        response = self.client.patch(nonexistent_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReviewDeletionTests(APITestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user(
            username='reviewer', password='testpass')
        UserProfileModel.objects.create(
            user=self.reviewer, user_type='customer')

        self.business_user = User.objects.create_user(
            username='business', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.other_user = User.objects.create_user(
            username='other', password='testpass')
        UserProfileModel.objects.create(
            user=self.other_user, user_type='customer')

        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Gute Arbeit!'
        )
        self.url = reverse('reviews-detail', args=[self.review.id])

    def test_reviewer_can_delete_review(self):
        self.client.force_authenticate(user=self.reviewer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_reviewer_cannot_delete_review(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_review(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_nonexistent_review(self):
        self.client.force_authenticate(user=self.reviewer)
        nonexistent_url = reverse('reviews-detail', args=[999999])
        response = self.client.delete(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
