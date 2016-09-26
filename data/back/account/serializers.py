from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.contrib.auth.password_validation import validate_password as vp
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models
from snapshot.models import Photo, FollowUser, Photo
from catalog.models import Promotion
from catalog.serializers import EventSerializer


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.State


class CitySerializer(serializers.ModelSerializer):

    state = StateSerializer()

    class Meta:
        model = models.City


class DistrictSerializer(serializers.ModelSerializer):

    city = CitySerializer()

    class Meta:
        model = models.District


class StoreShortSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='brand_name', read_only=True)
    thumb = serializers.ImageField(source='crop', read_only=True)

    class Meta:
        model = models.Store
        fields = ('pk', 'username', 'thumb')
        extra_kwargs = {'pk': {'read_only': True}}


class VendorStoreSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='store.brand_name', read_only=True)
    thumb = serializers.ImageField(source='store.thumb', read_only=True)

    class Meta:
        model = models.Vendor
        fields = ('pk', 'username', 'thumb')
        extra_kwargs = {'pk': {'read_only': True}}


class StoreSerializer(serializers.ModelSerializer):

    location = serializers.CharField(source='get_location', read_only=True)
    # It automatically serialize next data to the dict (district)
    district_title = serializers.CharField(source='district.title')
    city_title = serializers.CharField(source='district.city.title')
    state_title = serializers.CharField(source='district.city.state.title')
    follower_count = serializers.SerializerMethodField(read_only=True)
    photo_count = serializers.SerializerMethodField(read_only=True)
    newest_promotion = serializers.SerializerMethodField(read_only=True)
    events = EventSerializer(source='event_set', many=True, read_only=True)

    def create(self, validated_data):
        with transaction.atomic():
            district_args = validated_data.pop('district')
            city_args = district_args.pop('city')
            state_args = city_args.pop('state')

            state, _ = models.State.objects.get_or_create(**state_args)

            city_args['state'] = state

            city, c = models.City.objects.get_or_create(**city_args)

            district_args['city'] = city

            district, c = models.District.objects.get_or_create(
                **district_args)

            validated_data['district'] = district
            vendor_id = validated_data.pop('vendor')
            store = self.Meta.model.objects.create(vendor_id=vendor_id,
                                                   **validated_data)
            return store

    def update(self, instance, validated_data):
        with transaction.atomic():
            district_args = validated_data.pop('district', None)

            if 'vendor' in validated_data:
                validated_data.pop('vendor')

            for k, v in validated_data.items():
                setattr(instance, k, v)

            if district_args:
                self.check_key_title('district', **district_args)
                try:
                    city_args = district_args.pop('city')
                    self.check_key_title('city', **city_args)

                    state_args = city_args.pop('state')

                    state, c = models.State.objects.get_or_create(**state_args)
                    self.check_key_title('state', **state_args)

                    city_args['state'] = state

                    city, c = models.City.objects.get_or_create(**city_args)

                    district_args['city'] = city
                except KeyError as e:
                    raise serializers.ValidationError(
                        {e.message: _('This field is required.')})
                district, c = models.District.objects.get_or_create(
                    **district_args)

                instance.district = district
            instance.save()

        return instance

    def get_follower_count(self, obj):
        return FollowUser.objects.filter(user_id=obj.vendor_id).count()

    def get_photo_count(self, obj):
        return Photo.objects.filter(visitor_id=obj.vendor_id).count()

    def get_newest_promotion(self, obj):
        promotion = obj.promotion_set.first()
        if promotion:
            return promotion.post.url

    def check_key_title(self, key, **kwargs):
        if 'title' not in kwargs:
            raise serializers.ValidationError(
                {key: _('This field is required.')})

    class Meta:
        model = models.Store
        extra_kwargs = {'district': {'read_only': True}}


class StorePhotoSerializer(serializers.ModelSerializer):
    """Serializer for photo detail page. It provides a location string,
    and probably set of photos."""
    location = serializers.CharField(source='get_location', read_only=True)
    overview = serializers.SerializerMethodField(read_only=True)

    def get_overview(self, obj):
        qs = obj.vendor.user.photo_set.all()[:4]
        serializer = PhotoCropSerializer(instance=qs, many=True,
                                         context=self.context)
        return serializer.data

    class Meta:
        model = models.Store


class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Vendor


class UserCreateSerializer(serializers.ModelSerializer):
    """ Serializer for creating new profile """
    url = serializers.HyperlinkedIdentityField(view_name='account:profile-detail')
    confirm_password = serializers.CharField(allow_blank=False, write_only=True)
    vendor = VendorSerializer()

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password':
                                                   _('Passwords do not match')})
        return attrs

    def validate_password(self, value):
        """ Validate password with django password validation """
        vp(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        vendor_args = validated_data.pop('vendor', None)
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        models.Vendor.objects.create(user=user, **vendor_args)
        return user

    class Meta:
        model = get_user_model()
        exclude = ('is_staff', 'is_superuser', 'is_active', 'groups',
                   'user_permissions', )
        write_only_fields = ('password',)
        read_only_fields = ('date_joined', 'last_login')


class UserUpdateSerializer(serializers.ModelSerializer):
    """ Serializer for update account """
    vendor = VendorSerializer()

    def update(self, instance, validated_data):
        vendor_args = validated_data.pop('vendor', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if vendor_args:
            vendor_args.pop('user')
            models.Vendor.objects.update_or_create(user=instance, defaults=vendor_args)
        return instance

    class Meta:
        model = get_user_model()
        exclude = ('is_staff', 'is_superuser', 'is_active', 'groups',
                   'user_permissions', 'password',)
        read_only_fields = ('date_joined', 'last_login')


class UserPasswordSerializer(serializers.ModelSerializer):
    """ Serializer for resetting user`s password """
    confirm_password = serializers.CharField(allow_blank=False, write_only=True)
    new_password = serializers.CharField(allow_blank=False, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password':
                                                   _('Passwords do not match')})
        return attrs

    def validate_password(self, value):
        vp(value)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    class Meta:
        model = get_user_model()
        fields = ('password', 'confirm_password', 'new_password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('username',)


class VendorBriefSerializer(serializers.ModelSerializer):
    """ Used only for the 'get my vendor' view and login view.
    Now store pk equals vendor pk """
    username = serializers.CharField(source='user.username', read_only=True)
    brand_name = serializers.CharField(source='store.brand_name', read_only=True,
                                       allow_null=True, allow_blank=True)
    photo_count = serializers.IntegerField(source='user.photo_set.count',
                                           read_only=True)
    group_count = serializers.IntegerField(source='user.group_set.count',
                                           read_only=True)
    store = serializers.PrimaryKeyRelatedField(read_only=True)
    avatar = serializers.ImageField(source='store.photo', read_only=True)
    thumb = serializers.ImageField(source='store.crop', read_only=True)

    def get_chat_login(self, obj):
        if all(ord(c) < 128 for c in obj.user.username):
            return obj.user.username
        return obj.user.username.encode("hex")

    class Meta:
        model = models.Vendor
        fields = ('pk', 'thumb', 'avatar', 'username', 'brand_name',
                  'group_count', 'photo_count', 'store', )


class PhotoCropSerializer(serializers.ModelSerializer):
    """ Works for GroupListSerializer.
    Needed to get cropped photos from store (and group)."""
    crop = serializers.SerializerMethodField(read_only=True)
    # TODO: duplicated. Remove duplicate.
    # TODO: optimize code

    def get_crop(self, obj):
        photo = obj
        if photo and photo.original:
            photo = photo.original
        if photo and photo.crop.name:
            request = self.context.get('request', None)
            url = photo.crop.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return

    class Meta:
        model = Photo
        fields = ('id', 'crop')
