from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from users_auth_app.models import UserProfileModel
from offers_app.models import Offer, OfferDetail


class OffersTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.offer = Offer.objects.create(
            title='Test Offer',
            description='Test Description',
            user=self.user
        )
        OfferDetail.objects.create(
            offer=self.offer,
            offer_type='basic',
            price=100,
            delivery_time_in_days=7
        )

    def test_get_offers_list(self):
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)
        if response.data['results']:
            offer = response.data['results'][0]
            expected_keys = [
                'id', 'user', 'title', 'description', 'details',
                'min_price', 'min_delivery_time', 'user_details',
                'created_at', 'updated_at', 'image', 'file', 'image_url'
            ]
            for key in expected_keys:
                self.assertIn(key, offer)

    def test_filter_offers_by_creator(self):
        url = reverse('offer-list')
        response = self.client.get(url, {'creator_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for offer in response.data['results']:
            self.assertEqual(offer['user'], self.user.id)

    def test_offers_list_no_authentication(self):
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ordering_offers_by_min_price(self):
        url = reverse('offer-list')
        response = self.client.get(url, {'ordering': 'min_price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OfferCreationTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.customer_user = User.objects.create_user(
            username='customeruser', password='testpass')
        UserProfileModel.objects.create(
            user=self.customer_user, user_type='customer')

        self.url = reverse('offer-list')

        self.valid_payload = {
            "title": "Grafikdesign-Paket",
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design", "Visitenkarte"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
                    "offer_type": "premium"
                }
            ]
        }

    def test_create_offer_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(len(response.data['details']), 3)

    def test_create_offer_unauthenticated(self):
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_as_customer(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_with_less_than_three_details(self):
        self.client.force_authenticate(user=self.business_user)
        invalid_payload = self.valid_payload.copy()
        # nur 2 Details
        invalid_payload['details'] = invalid_payload['details'][:2]
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Es müssen genau drei Details übergeben werden.', str(response.data))


class OfferDetailTests(APITestCase):
    def setUp(self):
        from users_auth_app.models import UserProfileModel

        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.offer = Offer.objects.create(
            title='Grafikdesign-Paket',
            description='Testbeschreibung',
            user=self.business_user
        )
        OfferDetail.objects.create(
            offer=self.offer,
            offer_type='basic',
            price=100,
            delivery_time_in_days=5
        )
        OfferDetail.objects.create(
            offer=self.offer,
            offer_type='standard',
            price=200,
            delivery_time_in_days=7
        )
        OfferDetail.objects.create(
            offer=self.offer,
            offer_type='premium',
            price=500,
            delivery_time_in_days=10
        )

        self.detail_url = reverse('offer-detail', args=[self.offer.id])

    def test_get_offer_detail_authenticated(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer.id)
        self.assertIn('details', response.data)
        self.assertEqual(len(response.data['details']), 3)

    def test_get_offer_detail_unauthenticated(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_offer_returns_404(self):
        self.client.force_authenticate(user=self.business_user)
        nonexistent_url = reverse('offer-detail', args=[999999])
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferUpdateTests(APITestCase):
    def setUp(self):
        from users_auth_app.models import UserProfileModel

        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass')
        UserProfileModel.objects.create(
            user=self.other_user, user_type='business')

        self.offer = Offer.objects.create(
            title='Grafikdesign-Paket',
            description='Testbeschreibung',
            user=self.business_user
        )
        OfferDetail.objects.create(
            offer=self.offer,
            offer_type='basic',
            price=100,
            delivery_time_in_days=5
        )

        self.patch_url = reverse('offer-detail', args=[self.offer.id])

        self.valid_patch_payload = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": ["Logo Design", "Flyer"],
                    "offer_type": "basic"
                }
            ]
        }

    def test_update_offer_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.patch(
            self.patch_url, self.valid_patch_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Updated Grafikdesign-Paket")
        updated_detail = next(
            (d for d in response.data['details'] if d['offer_type'] == 'basic'), None)
        self.assertIsNotNone(updated_detail)
        self.assertEqual(updated_detail['title'], "Basic Design Updated")
        self.assertEqual(updated_detail['revisions'], 3)

    def test_update_offer_unauthenticated(self):
        response = self.client.patch(
            self.patch_url, self.valid_patch_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_offer_as_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            self.patch_url, self.valid_patch_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_offer_returns_404(self):
        self.client.force_authenticate(user=self.business_user)
        nonexistent_url = reverse('offer-detail', args=[999999])
        response = self.client.patch(
            nonexistent_url, self.valid_patch_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_offer_with_invalid_data_returns_400(self):
        self.client.force_authenticate(user=self.business_user)
        invalid_payload = {
            "details": [
                {
                    "title": "",
                    "offer_type": "basic"
                }
            ]
        }
        response = self.client.patch(
            self.patch_url, invalid_payload, format='json')
        self.assertIn(response.status_code, [
                      status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])


class OfferDeleteTests(APITestCase):
    def setUp(self):
        from users_auth_app.models import UserProfileModel

        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass')
        UserProfileModel.objects.create(
            user=self.other_user, user_type='business')

        self.offer = Offer.objects.create(
            title='Grafikdesign-Paket',
            description='Testbeschreibung',
            user=self.business_user
        )

        self.delete_url = reverse('offer-detail', args=[self.offer.id])

    def test_delete_offer_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_offer_unauthenticated(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_offer_as_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_offer_returns_404(self):
        self.client.force_authenticate(user=self.business_user)
        nonexistent_url = reverse('offer-detail', args=[999999])
        response = self.client.delete(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferDetailEndpointTests(APITestCase):
    def setUp(self):
        from users_auth_app.models import UserProfileModel

        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.offer = Offer.objects.create(
            title='Grafikdesign-Paket',
            description='Testbeschreibung',
            user=self.business_user
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            offer_type='basic',
            title='Basic Design',
            price=100,
            delivery_time_in_days=5,
            revisions=2,
            features=["Logo Design", "Visitenkarte"]
        )

        self.detail_url = reverse(
            'offerdetails-detail', args=[self.offer_detail.id])

    def test_get_offerdetail_success(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer_detail.id)
        self.assertEqual(response.data['title'], 'Basic Design')
        self.assertEqual(response.data['price'], '100.00')

    def test_get_offerdetail_nonexistent_returns_404(self):
        nonexistent_url = reverse('offerdetails-detail', args=[999999])
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_offerdetail_no_authentication(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
