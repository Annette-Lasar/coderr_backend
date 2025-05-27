from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from users_auth_app.models import UserProfileModel
from orders_app.models import Order
from offers_app.models import Offer, OfferDetail


class OrdersTests(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            username='customeruser', password='testpass')
        UserProfileModel.objects.create(
            user=self.customer_user, user_type='customer')

        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.other_customer = User.objects.create_user(
            username='othercustomer', password='testpass')
        UserProfileModel.objects.create(
            user=self.other_customer, user_type='customer')

        offer_detail = OfferDetail.objects.create(
            offer=Offer.objects.create(
                title='Grafikdesign-Paket',
                description='Testbeschreibung',
                user=self.business_user
            ),
            offer_type='basic',
            title='Basic Design',
            price=100,
            delivery_time_in_days=5,
            revisions=2,
            features=["Logo Design", "Visitenkarte"]
        )

        self.order1 = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            offer_detail=offer_detail,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress'
        )

        self.order2 = Order.objects.create(
            customer_user=self.other_customer,
            business_user=self.business_user,
            offer_detail=offer_detail,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress'
        )

        self.url = reverse('orders-list')

    def test_get_orders_as_customer(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for order in response.data:
            self.assertIn(order['customer_user'], [
                          self.customer_user.id, self.other_customer.id])
            self.assertTrue(
                order['customer_user'] == self.customer_user.id or
                order['business_user'] == self.customer_user.id
            )

    def test_get_orders_as_business_user(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for order in response.data:
            self.assertEqual(order['business_user'], self.business_user.id)

    def test_get_orders_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderCreationTests(APITestCase):
    def setUp(self):
        from offers_app.models import Offer, OfferDetail

        self.customer_user = User.objects.create_user(
            username='customeruser', password='testpass')
        UserProfileModel.objects.create(
            user=self.customer_user, user_type='customer')

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

        self.url = reverse('orders-list')

    def test_create_order_success(self):
        self.client.force_authenticate(user=self.customer_user)
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_user'], self.customer_user.id)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['title'], self.offer_detail.title)

    def test_create_order_unauthenticated(self):
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_as_business_user_forbidden(self):
        self.client.force_authenticate(user=self.business_user)
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_invalid_offer_detail(self):
        self.client.force_authenticate(user=self.customer_user)
        data = {'offer_detail_id': 999999}  # nicht existent
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderStatusUpdateTests(APITestCase):
    def setUp(self):
        from offers_app.models import Offer, OfferDetail

        self.customer_user = User.objects.create_user(
            username='customeruser', password='testpass')
        UserProfileModel.objects.create(
            user=self.customer_user, user_type='customer')

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

        self.order = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            offer_detail=self.offer_detail,
            title=self.offer_detail.title,
            revisions=self.offer_detail.revisions,
            delivery_time_in_days=self.offer_detail.delivery_time_in_days,
            price=self.offer_detail.price,
            features=self.offer_detail.features,
            offer_type=self.offer_detail.offer_type,
            status='in_progress'
        )

        self.url = reverse('orders-detail', args=[self.order.id])

    def test_update_order_status_success(self):
        self.client.force_authenticate(user=self.business_user)
        data = {'status': 'completed'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_update_order_status_invalid_status(self):
        self.client.force_authenticate(user=self.business_user)
        data = {'status': 'invalid_status'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_unauthenticated(self):
        data = {'status': 'completed'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_order_status_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer_user)
        data = {'status': 'completed'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_status_not_found(self):
        self.client.force_authenticate(user=self.business_user)
        # Nicht existierende Order-ID
        url = reverse('orders-detail', args=[999999])
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderDeletionTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin', password='adminpass', is_staff=True)
        self.business_user = User.objects.create_user(
            username='business', password='businesspass')
        self.customer_user = User.objects.create_user(
            username='customer', password='customerpass')

        offer = Offer.objects.create(
            user=self.business_user, title='Test Offer')
        offer_detail = OfferDetail.objects.create(
            offer=offer, title='Basic', price=100, delivery_time_in_days=5)

        self.order = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            offer_detail=offer_detail,
            title='Basic Order',
            revisions=3,
            delivery_time_in_days=5,
            price=100,
            features=['Logo', 'Visitenkarte'],
            offer_type='basic'
        )

        self.url = reverse('orders-detail', args=[self.order.id])

    def test_admin_can_delete_order(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_admin_cannot_delete_order(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_order(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderCountViewTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='business', password='businesspass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='customerpass')
        UserProfileModel.objects.create(
            user=self.customer_user, user_type='customer')

        offer = Offer.objects.create(
            user=self.business_user, title='Test Offer')
        offer_detail = OfferDetail.objects.create(
            offer=offer, title='Basic', price=100, delivery_time_in_days=5)

        for _ in range(3):
            Order.objects.create(
                customer_user=self.customer_user,
                business_user=self.business_user,
                offer_detail=offer_detail,
                title='Basic Order',
                revisions=3,
                delivery_time_in_days=5,
                price=100,
                features=['Logo', 'Visitenkarte'],
                offer_type='basic',
                status='in_progress'
            )

        for _ in range(2):
            Order.objects.create(
                customer_user=self.customer_user,
                business_user=self.business_user,
                offer_detail=offer_detail,
                title='Completed Order',
                revisions=3,
                delivery_time_in_days=5,
                price=100,
                features=['Logo', 'Visitenkarte'],
                offer_type='basic',
                status='completed'
            )

        self.url = reverse('order-count', args=[self.business_user.id])

    def test_get_in_progress_order_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('order_count', response.data)
        self.assertEqual(response.data['order_count'], 3)

    def test_invalid_business_user_returns_404(self):
        invalid_url = reverse('order-count', args=[999999])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CompletedOrderCountTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass')
        UserProfileModel.objects.create(
            user=self.business_user, user_type='business')

        self.customer_user = User.objects.create_user(
            username='customeruser', password='testpass')
        UserProfileModel.objects.create(
            user=self.customer_user, user_type='customer')

        offer = Offer.objects.create(
            title='Test Offer', user=self.business_user)
        offer_detail = OfferDetail.objects.create(
            offer=offer, title='Basic', price=100, delivery_time_in_days=5)

        Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            offer_detail=offer_detail,
            title='Completed Order',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo'],
            offer_type='basic',
            status='completed'
        )

        Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            offer_detail=offer_detail,
            title='In Progress Order',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo'],
            offer_type='basic',
            status='in_progress'
        )

        self.url = reverse('completed-order-count',
                           args=[self.business_user.id])

    def test_get_completed_order_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)

    def test_nonexistent_business_user(self):
        url = reverse('completed-order-count', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
