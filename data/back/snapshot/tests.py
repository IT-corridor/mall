from __future__ import unicode_literals, absolute_import

import os
import hashlib
import time
import unittest
from django.core.urlresolvers import reverse
from django.core.files.base import File
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db import connection
from rest_framework.test import APITestCase, APIClient
from .models import Mirror, Group, Member, Tag, Photo, Like, Link
from visitor.models import Visitor
from account.models import Vendor, Store, District, City, State
from catalog import models as c_models
from catalog import tests as c_tests

# TODO: CREATE TEST CASES!
DB_VENDOR = connection.vendor

visitor_data_1 = {"weixin": "oRFOiwzjygVD6hwtyMFUZCZ299bo",
                  "access_token": "ACCESS_TOKEN",
                  "refresh_token": "REFRESH_TOKEN",
                  "expires_in": 7200,
                  "token_date": "2016-06-15T07:08:04.960Z"}

visitor_data_2 = {"weixin": "oRFOiwzjygVD6hwtyMFUZCZ299b1",
                  "access_token": "ACCESS_TOKEN",
                  "refresh_token": "REFRESH_TOKEN",
                  "expires_in": 7200,
                  "token_date": "2016-06-15T07:08:04.960Z"}

visitor_data_3 = {"weixin": "oRFOiwzjygVD6hwtyMFUZCZ299b2",
                  "access_token": "ACCESS_TOKEN",
                  "refresh_token": "REFRESH_TOKEN",
                  "expires_in": 7200,
                  "token_date": "2016-06-15T07:08:04.960Z"}

filepath = os.path.join(settings.MEDIA_ROOT, 'image.jpeg')


class MirrorTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user_1 = User.objects.create(username='Nikolay')
        user_2 = User.objects.create(username='Jack')

        Visitor.objects.create(user=user_1)
        Visitor.objects.create(user=user_2)

        cls.vendor_data_1 = {'weixin': 'oRFOiwzjygVD6hwtyMFUZCZ299bo'}
        cls.vendor_data_2 = {'weixin': 'oRFOiwzjygVD6hwtyMFUZCZ299b1'}
        url = reverse('visitor:login')
        client = APIClient()
        response = client.post(url, data=cls.vendor_data_1)
        assert response.status_code == 200
        client.logout()

        response = client.post(url, data=cls.vendor_data_2)
        assert response.status_code == 200
        client.logout()

        cls.visitor_1 = Visitor.objects.get(pk=1)
        cls.visitor_2 = Visitor.objects.get(pk=2)
        cls.data_1 = {'title': 'first mirror', 'location': 'china sanlitun',
                      'is_locked': False, 'latitude': 22.299439,
                      'longitude': 114.173881, 'owner': cls.visitor_1,
                      'token': 'AqVlo9fwZJP66WHQBxsL0qMGq507aHBkO0lC3MS5'}

        cls.data_2 = {'title': 'opplya', 'location': 'beijing',
                      'is_locked': False, 'latitude': 39.929344,
                      'longitude': 116.48178, 'owner': cls.visitor_2,
                      'token': 'Ar3dltB4VSVwaasOfRkJbPojq28Q2dzxC1vZ1TczDQBH'}

        cls.data_3 = {'title': 'opzlya', 'location': 'beijing',
                      'is_locked': False, 'latitude': 39.929344,
                      'longitude': 116.48178, 'owner': cls.visitor_2,
                      'token': 'Ar3dltB4VSVwaasOfRkJbPojq28Q2dzxC1vZ1TczDsBH'}

        cls.mirror_1 = Mirror.objects.create(**cls.data_1)
        cls.mirror_2 = Mirror.objects.create(**cls.data_2)
        cls.mirror_3 = Mirror.objects.create(**cls.data_3)

        cls.now = time.time()
        key = "sdlfkj9234kjlnzxcv90123098123asldjk"
        cls.checksum = hashlib.md5('{}{}'.format(key, cls.now)).hexdigest()

    def test_mirror_last_login(self):
        self.mirror_1.update_last_login()
        self.assertTrue(self.mirror_1.is_online())

    def test_mirror_locked(self):
        self.mirror_1.lock()
        self.assertTrue(self.mirror_1.is_locked)
        self.assertTrue(self.mirror_1.is_overtime())

    def test_mirrors_locked_then_unlock(self):
        Mirror.objects.all().lock()
        locked = Mirror.objects.all()
        for mirror in locked:
            self.assertTrue(mirror.is_locked)

        Mirror.objects.all().unlock()
        unlocked = Mirror.objects.all()
        for mirror in unlocked:
            self.assertFalse(mirror.is_locked)

    @unittest.skipIf(DB_VENDOR == 'sqlite', 'SQRT not supported')
    def test_nearest_mirrors(self):
        mirrors = Mirror.objects.get_by_distance(39.929344, 116.48178)

        self.assertTrue(len([x for x in mirrors]) == 2)

    def test_mirror_view_unlock(self):
        self.force_login()
        response = self.client.post(reverse('snapshot:mirror-unlock'))

        self.assertEqual(response.status_code, 200)
        self.client.logout()

    @unittest.skipIf(DB_VENDOR == 'sqlite', 'SQRT not supported')
    def test_mirror_view_list(self):
        self.force_login()
        response = self.client.get(reverse('snapshot:mirror-list'))

        self.assertEqual(response.status_code, 200)
        self.client.logout()

    @unittest.skip("It works. just skippend")
    def test_mirror_view_detail(self):

        self.force_login()
        Mirror.objects.lock()
        time.sleep(61)
        response = self.client.get(reverse('snapshot:mirror-detail',
                                           kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_mirror_view_update(self):
        self.force_login()
        response = self.client.patch(reverse('snapshot:mirror-detail',
                                           kwargs={'pk': 2}))

        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_mirror_view_status(self):

        data = {'token': 'Ar3dltB4VSVwaasOfRkJbPojq28Q2dzxC1vZ1TczDQBH',
                'timestamp': self.now,
                'checksum': self.checksum,
        }
        self.force_login()
        response = self.client.post(reverse('snapshot:mirror-status'),
                                    data=data)

        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_create_mirror(self):

        data = {'token': 'weixin',
                'latitude': 10,
                'longitude': 10,
                'title': 'iSmarror for e.g.',
                'timestamp': self.now,
                'checksum': self.checksum}
        url = reverse('snapshot:mirror-list')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)

    def force_login(self):
        user = User.objects.get(id=2)
        self.client.force_login(user=user)


class GroupTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create(username="Nikolay")
        user_1 = Visitor.objects.create(user=cls.owner)

        cls.member = User.objects.create(username="Jack")
        user_2 = Visitor.objects.create(user=cls.member)

        cls.member_2 = User.objects.create(username="Peter")
        user_3 = Visitor.objects.create(user=cls.member_2)

        cls.group = Group.objects.create(owner=cls.owner, title='group 0')
        cls.group_private = Group.objects.create(owner=cls.owner, title='G 0',
                                                 is_private=True)
        cls.group_cln = Group.objects.create(owner=cls.member, title='Clones')
        Member.objects.create(visitor=cls.member, group=cls.group_private)
        Tag.objects.create(title='Primal', visitor=cls.owner, group=cls.group)
        Tag.objects.create(title='Second', visitor=cls.member,
                           group=cls.group_private)

    def test_list_group_as_owner(self):
        self.list_group(1, count=3)

    def test_list_group_as_member(self):
        self.list_group(2, count=3)

    def test_list_group_as_not_member(self):
        self.list_group(3, count=2)

    def test_list_group_as_anon(self):
        self.list_group(expected_code=403)

    def test_create_group(self):
        """ Test creating public group """
        data = {'title': 'test group'}
        self.force_login(1)
        url = reverse('snapshot:group-list')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_access_group(self):
        """Access to the public group for not authenticated person """
        url = reverse('snapshot:group-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_access_group_private(self):
        """Test access to the private group from not authenticated person.
        Expect 403 Forbidden."""
        url = reverse('snapshot:group-detail', kwargs={'pk': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_access_group_private_member(self):
        """Test access to the private group from member."""
        self.force_login(2)
        url = reverse('snapshot:group-detail', kwargs={'pk': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_delete_group(self):
        """Test delete group as group owner """
        self.force_login(1)
        url = reverse('snapshot:group-detail', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.client.logout()

    def test_delete_group_as_member(self):
        """Test delete group as group member. Expect 403 Forbidden. """
        self.force_login(2)
        url = reverse('snapshot:group-detail', kwargs={'pk': 2})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_update_put_as_member(self):
        """ Attempt to update whole group. Expect 403 Forbidden."""
        self.force_login(2)
        url = reverse('snapshot:group-detail', kwargs={'pk': 2})
        response = self.client.put(url, data={'title': 'New title'})
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_update_patch_as_member(self):
        """ Attempt to update group partially.
        Expect 403 for member / collaborator """
        self.force_login(2)
        url = reverse('snapshot:group-detail', kwargs={'pk': 2})
        response = self.client.patch(url, data={'title': 'New title'})
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_create_tag_for_group(self):
        """ Add tag as group owner """
        self.force_login(1)
        url = reverse('snapshot:group-tag-create', kwargs={'pk': 2})
        response = self.client.post(url, data={'title': 'new tag'})
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_create_tag_member_for_group(self):
        """ Add tag as group member """
        self.force_login(2)
        url = reverse('snapshot:group-tag-create', kwargs={'pk': 2})
        response = self.client.post(url, data={'title': 'new tag2'})
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_update_tag_group(self):
        self.force_login(1)
        url = reverse('snapshot:tag-detail', kwargs={'pk': 1})
        response = self.client.patch(url, data={'title': 'updated'})
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_delete_group_tag(self):
        """ Delete tag as group owner """
        self.force_login(1)
        url = reverse('snapshot:tag-detail', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.client.logout()

    def test_update_tag_group_member(self):
        """Expect 403."""
        self.force_login(2)
        url = reverse('snapshot:tag-detail', kwargs={'pk': 1})
        response = self.client.patch(url, data={'title': 'updated'})
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_delete_tag_group_member(self):
        """ Expect 403 """
        self.force_login(2)
        url = reverse('snapshot:tag-detail', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_delete_tag_group_member_own(self):
        self.force_login(2)
        url = reverse('snapshot:tag-detail', kwargs={'pk': 2})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.client.logout()

    def test_add_member_to_group(self):
        self.force_login(1)
        url = reverse('snapshot:group-member-add', kwargs={'pk': 2})
        response = self.client.post(url, data={'username': 'Peter'})
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_remove_member_from_group(self):
        self.force_login(1)
        url = reverse('snapshot:group-member-remove', kwargs={'pk': 2})
        response = self.client.post(url, data={'member': 1})
        self.assertEqual(response.status_code, 204)
        self.client.logout()

    def test_add_photo_as_group_owner(self):
        """ Expect success. """
        self.photo_upload_and_delete(1)

    def test_add_photo_as_group_member(self):
        """ Expect success. """
        self.photo_upload_and_delete(2)

    def test_add_photo_as_not_group_member(self):
        """ Attempt to create a photo in the group
        not being a group member. """
        self.photo_upload_and_delete(3, expect_create=403, expect_delete=404)

    def test_add_photo_as_anon(self):
        """ Expect fail. """
        self.photo_upload_and_delete(expect_create=403, expect_delete=403)

    def photo_upload_and_delete(self, visitor_id=None, expect_create=201,
                                expect_delete=204):
        """ Testing file upload. Request must be multipart.
        After upload remove it. """
        if visitor_id:
            self.force_login(visitor_id)
        url = reverse('snapshot:group-photo-create', kwargs={'pk': 2})

        with open(filepath, 'r') as fp:
            data = {'title': 'Group2', 'photo': fp, 'description': 'Test'}

            response = self.client.post(url, data=data, format='multipart')
            self.assertEqual(response.status_code, expect_create)

        url = reverse('snapshot:photo-g-detail', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, expect_delete)
        if visitor_id:
            self.client.logout()

    def test_photo_list_group_owner(self):
        self.list_photo(1)

    def test_photo_list_group_member(self):
        self.list_photo(2)

    def test_photo_list_not_group_member(self):
        self.list_photo(3, expected_code=403)

    def test_photo_list_anon(self):
        self.list_photo(expected_code=403)

    def list_photo(self, visitor_id=None, expected_code=200):
        """ Test pagination """
        if visitor_id:
            self.force_login(visitor_id)
        for i in range(15):
            Photo.objects.create(title='test #{}'.format(i),
                                 group_id=2, visitor_id=2)

        url = reverse('snapshot:group-photo-list', kwargs={'pk': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected_code)
        if visitor_id:
            self.client.logout()

    def list_group(self, visitor_id=None, expected_code=200, count=2):
        """ Test pagination """
        if visitor_id:
            self.force_login(visitor_id)
        for i in range(15):
            Photo.objects.create(title='test #{}'.format(i),
                                 group_id=2, visitor_id=2)

        url = reverse('snapshot:group-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code == 200:
            self.assertEqual(response.data['count'], count)
        if visitor_id:
            self.client.logout()

    def force_login(self, pk):
        user = User.objects.get(id=pk)
        self.client.force_login(user=user)

    def test_photo_edit(self):
        Photo.objects.create(visitor=self.member)
        now = time.time()
        key = "sdlfkj9234kjlnzxcv90123098123asldjk"
        checksum = hashlib.md5('{}{}'.format(key, now)).hexdigest()
        data = {'timestamp': now, 'checksum': checksum, 'title': 'Hello'}
        url = reverse('snapshot:photo-detail', kwargs={'pk': 1})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)

    def test_create_group_with_member(self):
        data = {'title': 'test group', 'members': [2, 3]}
        self.force_login(1)
        url = reverse('snapshot:group-list')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_clone_photo(self):
        with open(filepath, 'r') as fp:

            photo = Photo.objects.create(photo=File(fp), group_id=2,
                                         title='Original', visitor_id=1)
            photo.save()
        self.force_login(2)
        url = reverse('snapshot:photo-clone', kwargs={'pk': 1})
        data = {'group': self.group_cln.id}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_group_short_list(self):
        self.force_login(2)
        url = reverse('snapshot:group-my-groups-short')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_like_photo(self):
        photo = Photo.objects.create(group_id=2, title='Original',
                                     visitor_id=1)
        photo.save()
        self.force_login(2)
        url = reverse('snapshot:photo-like', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_liked_list(self):

        """ Test list with liked photos """
        for i in range(15):
            photo = Photo.objects.create(visitor_id=1, title=str(i))
            Like.objects.create(visitor_id=1, photo_id=photo.id)

        self.force_login(1)
        url = reverse('snapshot:photo-liked-list')
        response = self.client.get(url)
        data = response.data
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['results']), 12)
        self.assertEqual(response.status_code, 200)
        self.client.logout()


class SnapshotVendorTests(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user_1 = User.objects.create(username='Magnus')
        vendor_1 = Vendor.objects.create(user=cls.user_1)
        cls.user_2 = User.objects.create(username='Felix')
        vendor_2 = Vendor.objects.create(user=cls.user_2)
        cls.user_3 = User.objects.create(username='Sen')
        vendor_3 = Vendor.objects.create(user=cls.user_3)

        cls.visitor = User.objects.create(username="Peter")
        Visitor.objects.create(user=cls.visitor)

        state = State.objects.create(title='Beijing')
        city = City.objects.create(title='Beijing', state=state)
        district = District.objects.create(title='Good one', city=city)

        data = dict(street='of flowers',
                 build_name='Roof of the world',
                 build_no='67',
                 apt='24',
                 )

        Store.objects.create(district=district, vendor=vendor_1,
                             brand_name='FFF', **data)

        Store.objects.create(district=district, vendor=vendor_2,
                             brand_name='Magnificent', **data)

        Store.objects.create(district=district, vendor=vendor_3,
                             brand_name='Magnifico', **data)

        c_models.Category.objects.bulk_create(
            tuple((c_models.Category(**data) for data in c_tests.CATEGORIES))
        )
        c_models.Kind.objects.bulk_create(
            (c_models.Kind(**data) for data in c_tests.KINDS)
        )
        c_models.Brand.objects.bulk_create(
            (c_models.Brand(store_id=cls.user_1.pk, **data)
             for data in c_tests.BRANDS)
        )
        c_models.Color.objects.bulk_create(
            (c_models.Color(**data) for data in c_tests.COLORS)
        )
        c_models.Size.objects.bulk_create(
            (c_models.Size(**data) for data in c_tests.SIZES)
        )

        c_models.Commodity.objects.bulk_create(
            (c_models.Commodity(store_id=cls.user_1.pk, **data)
             for data in c_tests.COMMODITIES)
        )
        cls.photo = Photo.objects.create(visitor_id=cls.user_1.pk,
                                          title='testphoto')

        Group.objects.create(title='store`s group', owner=cls.user_1)

    def test_create_group(self):
        """ Test creating public group """
        data = {'title': 'test group'}
        self.force_login(1)

        url = reverse('snapshot:group-list')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_add_member_vendor_to_group(self):
        self.force_login(1)
        url = reverse('snapshot:group-member-vendor-add', kwargs={'pk': 1})
        response = self.client.post(url, data={'username': 'Magnificent'})
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_vendor_store_list(self):
        self.force_login(1)
        url = reverse('snapshot:group-vendor-list')
        response = self.client.get(url, data={'q': 'Magni'})
        data = response.data
        self.assertEqual(len(data), 2)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_add_links_as_owner(self):
        self.add_links_to_commodity(1, 201)

    def test_add_links_as_not_owner(self):
        self.add_links_to_commodity(2, 403)

    def test_add_links_as_not_visitor(self):
        self.add_links_to_commodity(self.visitor.pk, 403)

    def test_remove_link_as_owner(self):
        self.remove_link(1, 204)

    def test_remove_link_as_not_owner(self):
        self.remove_link(2, 403)

    def test_remove_link_as_not_visitor(self):
        self.remove_link(self.visitor.pk, 403)

    def add_links_to_commodity(self, user_id, expected_code):
        """ Create a relation between photo and commodities. """
        self.force_login(user_id)

        url = reverse('snapshot:photo-add-links', kwargs={'pk': self.photo.pk})
        data = {'commodities': [1, 2]}
        self.force_login(user_id)

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, expected_code)

    def remove_link(self, user_id, expected_code):
        """ Removing link with commodity from photo"""
        self.force_login(user_id)
        link = Link.objects.create(photo_id=self.photo.pk, commodity_id=1)
        url = reverse('snapshot:photo-remove-link',
                      kwargs={'pk': self.photo.pk})
        data = {'link': link.pk}
        self.force_login(user_id)

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, expected_code)

    def force_login(self, pk):
        user = User.objects.get(id=pk)
        self.client.force_login(user=user)
