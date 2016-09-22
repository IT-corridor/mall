from __future__ import unicode_literals, absolute_import

import json
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

from account.models import Vendor, Store, District, City, State


# Create your tests here.
class VendorTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.admin_data = {'username': 'niklak', 'password': 'caesaR65', 'email': ''}
        cls.vendor_data = {'username': 'jack', 'password': 'proPer76'}
        cls.customer_data = {'username': 'peter', 'password': 'frAnKly12'}

        cls.admin = User.objects.create_superuser(**cls.admin_data)
        user = User.objects.create_user(**cls.vendor_data)
        cls.vendor = Vendor.objects.create(user=user)
        cls.customer = User.objects.create_user(**cls.customer_data)

    def test_admin_password(self):
        self.assertTrue(self.admin.check_password(self.admin_data['password']))

    def test_vendor_password(self):
        self.assertTrue(self.vendor.user.check_password(self.vendor_data['password']))

    def test_rest_login_success(self):
        """ Test login view for all accounts """
        user = self.vendor.user
        data_compare = {'username': user.username, 'id': user.id,
                        'store': None, 'brand_name': None, 'avatar': None,
                        'thumb': None, 'pk': 2,
                        'photo_count': 0, 'group_count': 0,
                        'chat_login': user.username
                        }
        url = reverse('account:login')
        response = self.client.post(url, data=self.vendor_data)
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(response.data, data_compare)

    def test_rest_login_error_400(self):
        """ Test login view for missing parameter """
        response = self.client.post(reverse('account:login'),
                                    data={'username': 'jack'})
        self.assertEqual(response.status_code, 400)

    def test_rest_login_error_401(self):
        """ Test """
        response = self.client.post(reverse('account:login'),
                                    data={'username': 'peter',
                                          'password': '12345'})

        self.assertEqual(response.status_code, 401)

    def test_rest_login_error_405(self):
        """ Test wrong request method for login view  """
        url = reverse('account:login')
        response = self.client.get(url, data=self.vendor_data)
        self.assertEqual(response.status_code, 405)


class StoreTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.vendor_data_1 = {'username': 'jack', 'password': 'proPer76'}
        cls.vendor_data_2 = {'username': 'john', 'password': 'groNasd12'}
        cls.customer_data = {'username': 'peter', 'password': 'frAnKly12'}
        vendor_1 = User.objects.create_user(**cls.vendor_data_1)
        vendor_2 = User.objects.create_user(**cls.vendor_data_2)
        cls.vendor_1 = Vendor.objects.create(user=vendor_1)
        cls.vendor_2 = Vendor.objects.create(user=vendor_2)
        cls.customer = User.objects.create_user(**cls.customer_data)

        state = State.objects.create(title='Shanghai')
        city = City.objects.create(title='Shanghai', state=state)
        district = District.objects.create(title='Good', city=city)

        cls.store = Store.objects.create(brand_name='EYE', apt='33',
                                         build_name='Checking',
                                         build_no='44', street='Good street',
                                         district=district,
                                         vendor=cls.vendor_2)
        # TEST CREATE HERE
        cls.data = {
            'brand_name': 'SMILE',
            'apt': '24',
            'build_no': '42',
            'build_name': 'High one',
            'street': 'Awesome',
            'street_no': '24',
            'district_title': 'First one',
            'city_title': 'Shanghai',
            'state_title': 'Shanghai',
            'name': 'Smile store #1'
        }

    def test_rest_login_success(self):
        """ Test login view for all accounts """
        user = self.vendor_2.user
        data_compare = {'username': user.username, 'id': user.id,
                        'store': self.store.pk, 'brand_name': 'EYE',
                        'avatar': None, 'thumb': None, 'pk': 2,
                        'photo_count': 0, 'group_count': 0,
                        'chat_login': user.username
                        }
        url = reverse('account:login')
        response = self.client.post(url, data=self.vendor_data_2)
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(response.data, data_compare)

    def test_create_vendor_store(self):

        self.client.login(username=self.vendor_data_1['username'],
                          password=self.vendor_data_1['password'])
        url = reverse('account:store-list')
        response = self.client.post(url, json.dumps(self.data),
                                    content_type='application/json')
        self.client.logout()
        self.assertEqual(response.status_code, 201)

    def test_update_vendor_store(self):

        data = {
            'brand_name': 'RUBY',
            'apt': '32',
            'build_no': '42',
            'build_name': 'Good',
            'street': 'Good street',
            'district_title': 'Super',
            'city_title': 'Beijing',
            'state_title': 'Beijing',
            'street_no': '67',
            'name': 'RUBY store',
        }
        self.client.login(username=self.vendor_data_2['username'],
                          password=self.vendor_data_2['password'])
        url = reverse('account:store-detail', kwargs={'pk': self.store.pk})
        response = self.client.put(url, json.dumps(data),
                                   content_type='application/json')
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_partial_update_vendor_store(self):

        data_0 = {
            'brand_name': 'ONYX',
        }
        # We are expecting, that if we change the city to the new,
        # than we have to change a district title, and state.
        # Complete location dict.

        data_2 = {
            'district': {
                'title': 'one',
                'city': {
                    'title': 'Tianjin',
                    'state': {
                        'title': 'Tianjin',
                    }
                },
            }
        }
        self.perform_patch(data_0)
        self.perform_patch(data_2)

    def perform_patch(self, data):
        self.client.login(username=self.vendor_data_2['username'],
                          password=self.vendor_data_2['password'])

        url = reverse('account:store-detail', kwargs={'pk': self.store.pk})
        response = self.client.patch(url, json.dumps(data),
                                     content_type='application/json')
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_expect_exception_store(self):
        self.access_store(self.vendor_data_1)
        self.access_store(self.customer_data)

    def access_store(self, user_data):
        self.client.login(username=user_data['username'],
                          password=user_data['password'])

        methods = ['post', 'put', 'patch', 'delete']
        url = reverse('account:store-detail', kwargs={'pk': self.store.pk})
        for method in methods:
            f = getattr(self.client, method)
            r = f(url)
            self.assertTrue(r.status_code in (403, 405))

        self.client.logout()

    def test_delete(self):
        self.client.login(username=self.vendor_data_2['username'],
                          password=self.vendor_data_2['password'])

        url = reverse('account:store-detail', kwargs={'pk': self.store.pk})
        response = self.client.delete(url, content_type='application/json')
        self.client.logout()
        self.assertEqual(response.status_code, 204)
