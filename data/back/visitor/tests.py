from __future__ import unicode_literals, absolute_import

import json
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

from visitor.models import Visitor, VisitorExtra, Weixin

# TODO: CREATE TEST CASES!


# Create your tests here.
class VisitorTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.data = {"openid": "oRFOiwzjygVD6hwtyMFUZCZ299bo",
                    "access_token": "ACCESS_TOKEN",
                    "refresh_token": "REFRESH_TOKEN",
                    "expires_in": 7200,
                    "token_date": "2016-06-15T07:08:04.960Z"}
        user = get_user_model().objects.create(username="Nikolay")
        visitor = Visitor.objects.create(user=user)
        weixin = Weixin.objects.create(visitor=visitor, unionid="123")
        VisitorExtra.objects.create(weixin=weixin, **cls.data)

    def test_rest_login_success(self):
        """ Test login view for all accounts """
        url = reverse('visitor:login')
        response = self.client.post(url, data={'weixin': self.data['openid']})
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_me(self):
        """ Test retreiving own weixin data """
        user = get_user_model().objects.first()
        self.client.force_login(user=user)
        url = reverse('visitor:me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()


class VisitorProfileTests(APITestCase):
    """ tEST FOR Visitor profiles """
    @classmethod
    def setUpTestData(cls):
        cls.data_create = {'username': 'Jack', 'phone': '11111111111',
                           'password': 'Greeeat12ss',
                           'confirm_password': 'Greeeat12ss'}
        cls.user_data = {'username': 'Nik', 'password': 'GrreaAe3456aa'}
        cls.visitor_data = {'phone': '12222222222'}
        cls.user = get_user_model()(username=cls.user_data['username'])
        cls.user.set_password(cls.user_data['password'])
        cls.user.save()

        Visitor.objects.create(username=cls.user_data['username'],
                               user=cls.user,
                               **cls.visitor_data)

    def test_registration(self):
        # Expected redirect = 400 bec ause we did not pass sms verification
        url = reverse('visitor:profile-list')
        response = self.client.post(url, self.data_create)
        self.assertEqual(response.status_code, 400)
        self.client.logout()

    def test_login(self):
        url = reverse('visitor:profile-login')
        data = {'password': self.user_data['password'],
                'phone': self.visitor_data['phone']}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_edit(self):
        self.client.force_login(self.user)
        url = reverse('visitor:profile-edit')
        data = {'username': 'Jackson'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_change_password(self):
        self.client.force_login(self.user)
        data = {'password': self.user_data['password'],
                'new_password': 'VectoraAdd3',
                'confirm_password': 'VectoraAdd3'}
        url = reverse('visitor:profile-change-password')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 204)
        self.client.logout()
