from __future__ import unicode_literals

import json
import logging
import pickle
import os
import datetime
from urlparse import urldefrag
from datetime import timedelta
from django.db import IntegrityError
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.db.models import F, Prefetch, Q, Count
from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Mirror, Photo, Comment, Tag, Member, Group, Like, Link, \
    FollowUser, FollowGroup, Article, Notification

from . import serializers
from .permissions import IsOwnerOrMember, MemberCanServe, \
    IsPhotoOwnerOrReadOnly
from .sutils import check_sign
from utils.views import OwnerCreateMixin, OwnerUpdateMixin, \
    VisitorCreateMixin, PaginationMixin
from utils.paginators import CustomPagination
from visitor.permissions import IsVisitor, IsVisitorOrVendor
from visitor.serializers import VisitorShortSerializer
from visitor.models import Visitor
from account.models import Vendor, Store
from account.serializers import VendorStoreSerializer, StoreShortSerializer
from catalog.models import Commodity, Event
from vutils.wzhifuSDK import JsApi_pub
from vutils.utils import get_last_day_of_month
from vutils.utils import get_nickname

# TODO: remove logger. it consumes resources
log = logging.getLogger(__name__)


# API VIEWSETS


class MirrorViewSet(viewsets.GenericViewSet):
    """ **Important**
        Currently not used.
    """
    serializer_class = serializers.MirrorSerializer
    permission_classes = [IsVisitor]

    def get_queryset(self):
        visitor = self.request.user.visitor
        return Mirror.objects.filter(owner=visitor, is_locked=True)

    @list_route(methods=['post'])
    def unlock(self, request, *args, **kwargs):
        """
        unlock the mirror

        omit_serializer: true
        omit_parameters:
            - form

        parameters:
            - name: mirror_id
              paramType: query

        """
        mirrors = self.get_queryset()
        if not mirrors:
            log.info('User {} has not locked devices '.format(request.user))
        else:
            # release all lock mirror of the user
            mirrors.unlock()
        return Response(status=200)

    def list(self, request):
        """
        get the most near mirrors
        ---
        # YAML (must be separated by `---`)

        parameters:
            - name: latitude
              paramType: query
            - name: longitude
              paramType: query
        """
        # todo real latitude longitude
        latitude = request.query_params.get('latitude', 0)
        longitude = request.query_params.get('longitude', 0)
        mirrors = Mirror.objects.get_by_distance(latitude, longitude)

        # TODO: optimize with db query!
        # online_mirrors = [i for i in mirrors if i.is_online()]
        # online_mirrors = [i for i in mirrors]

        # Mirror available if it is not locked or owner is current_user
        # Also mirror should be online.
        visitor = self.request.user
        a_mirrors = [i for i in mirrors if not i.is_locked or
                     i.owner_id == visitor.pk]
        # TODO remove next line
        serializer = serializers.MirrorSerializer(instance=a_mirrors, many=True)
        return Response(data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        lock mirror
        ---
        # YAML (must be separated by `---`)

        omit_serializer: true
        omit_parameters:
            - form
        """
        # THIS BLOCK TAKES NO SENSE HERE!!!
        mirrors = self.get_queryset()
        if not mirrors:
            # release all lock mirror of the user
            log.info('User {} has not locked devices '.format(request.user))
        else:
            mirrors.unlock()

        pk = kwargs.get('pk', None)
        if not pk:
            return Response(data={'error': _('Mirror id required')},
                            status=400)

        # LOOKS LIKE PRETTY PRETTY STUPID
        try:
            mirror = Mirror.objects.get(id=pk)

        except Mirror.DoesNotExist:
            log.warn('user provide mirror id is not existed')
            return Response(data={'error': _('Mirror does not exists')},
                            status=400)
        # mirror is  unlock  or the lock time is expired 1 minutes
        # todo if the mirror is offline return error
        if mirror.is_overtime():
            return Response(data={'error': _('Mirror is already locked')},
                            status=400)
        mirror.lock()
        # IT WILL REWRITE OWNER IF DIFFERENT PEOPLE USING MIRROR
        mirror.user = request.user
        mirror.save()
        serializer = serializers.MirrorSerializer(mirror)
        return Response(data=serializer.data, status=200)

    def retrieve(self, request, *args, **kwargs):
        """
        query a mirror is online
        ---
        omit_serializer: true
        omit_parameters:
            - form
        # THERE NEED TO PASS A PK PARAM!
        """
        status = 400
        pk = kwargs.get('pk', None)
        try:
            mirror = self.get_queryset().get(id=pk)
            if not mirror.is_online():
                data = {'error': _('Mirror is offline')}
            elif mirror.is_overtime():
                data = {'error': _('Mirror is unavailable')}
            else:
                serializer = serializers.MirrorSerializer(mirror)
                data = serializer.data
                status = 200
        except Mirror.DoesNotExist:
            data = {'error': _('Mirror not available')}

        return Response(data=data, status=status)

    @list_route(methods=['post'])
    def status(self, request, *args, **kwargs):
        """
        THIS REQUEST CALLED FROM ANDROID APP.
        Set a mirror online status.
        ---

        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: timestamp
              paramType: query
            - name: token
              paramType: query
            - name: checksum
              paramType: query

        """
        timestamp = request.data.get('timestamp', None)
        checksum = request.data.get('checksum', None)
        token = request.data.get('token', None)

        if not check_sign(timestamp, checksum):
            return Response(data={'error': _('Checksum error')}, status=400)
        log.info('sign correct')

        if not token:
            return Response(data={'error': _('Token is required')}, status=400)
        try:
            mirror = Mirror.objects.get(token=token)
        except Mirror.DoesNotExist:
            return Response(data={'error': _('Mirror token does not exist')})
        mirror.update_last_login()
        return Response(data={'status': True})

    def create(self, request, *args, **kwargs):
        """
        This request must be received only from android.
        It uses POST method.
        REQUEST PARAMS:
            check:
                checksum --- same as status request has. REQUIRED.
                timestamp --- same as status request has. REQUIRED.
            iSmarror data:
                token --- device token. REQUIRED.
                latitude --- latitude of the device. REQUIRED.
                longitude --- longitude of the device. REQUIRED.
                title --- title (name of device) --- NOT REQUIRED.
        If request is successful response will something like that:
            {u'title': u'iSmarror for e.g.', u'is_locked': False,
             u'longitude': u'10.0000000000',
             u'last_login': u'2016-06-13T10:02:14.011418Z',
             u'is_online': True, u'latitude': u'10.0000000000', u'id': 4}
        Response status in successful case is 201.
        In case of any error server will return 400 status and
        error description.
        An example of request:
        curl curl -H "Content-Type: application/json" -X \
        POST -d '{"checksum":"hexdigest_data_here","timestamp":"time", \
        "token": "mirror_token", "latitude": "10.23", "longitude": "10.23"}' \
        http://atyichu.cn/api/v1/mirror/
        But now we serving on atyichu.com. Keep in mind.
        """

        timestamp = request.data.pop('timestamp', None)
        checksum = request.data.pop('checksum', None)

        if not check_sign(timestamp, checksum):
            return Response(data={'error': _('Checksum error')}, status=400)

        serializer = serializers.MirrorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=201)


class ArticleViewSet(PaginationMixin, viewsets.ModelViewSet):
    # TODO: Dan put your permissions here
    permission_classes = ()

    def get_serializer_class(self):
        return serializers.ArticleListSerializer

    def get_queryset(self):
        qs = Article.objects.all()
        prefetch = Prefetch('photo_set', queryset=Photo.objects.all())

        qs = qs.prefetch_related(prefetch)
        return qs

    def create(self, request, *args, **kwargs):
        '''
        photos in data in form [23,43,242]
        '''
        data = request.data
        article = Article.objects.create(title=data['title'],
                                         description=data['description'],
                                         author=request.user)
        if 'photos' in data:
            for photo in data['photos']:
                Photo.objects.filter(id=photo).update(article=article)

        Event.objects.create(store_id=request.user.id,
                             type='article',
                             description='New article({}) is posted!'.format(data['title']))

        return Response(data={'id': article.id}, status=201)

    def update(self, request, *args, **kwargs):
        '''
        photos in data is in the array of photo objects
        '''
        data = request.data.copy()
        # remove original photos and add new ones
        Photo.objects.filter(article_id=data['id']).update(article=None)
        for item in data['photos']:
            Photo.objects.filter(id=item['id']).update(article_id=data['id'])

        return super(ArticleViewSet, self).update(request, args, kwargs)


class PhotoViewSet(PaginationMixin, viewsets.ModelViewSet):
    """ All about photos.
    """
    model = Photo
    serializer_class = serializers.PhotoDetailSerializer
    permission_classes = [IsPhotoOwnerOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', 'stamps__title')

    # TODO: test delete
    # TODO: maybe it is necessary to turn off pagination

    def get_queryset(self):
        # TODO: optimize
        qs = Photo.p_objects.select_related('original',
                                            'visitor__visitor')
        p = Prefetch('comment_set',
                     Comment.objects.select_related('author__visitor'))
        qs = qs.prefetch_related(p)
        if self.request.method == 'GET' and self.kwargs.get('pk'):
            qs = qs.prefetch_related('link_set__commodity__kind',
                                     'link_set__commodity__colors')
        return qs

    def get_serializer_class(self):
        if self.request.method == 'GET' and not self.kwargs.get('pk', None):
            return serializers.PhotoListSerializer
        return serializers.PhotoDetailSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a primary photo record without actual photo.
        Photo will be provided (as update) through android app.
        ---
        # YAML (must be separated by `---`)

        omit_serializer: true
        omit_parameters:
            - form
        """
        try:
            mirror = Mirror.objects.filter(user=request.user, is_lock=True)[0]
        except IndexError:
            return Response(data={'error': _('The mirror is unlocked')},
                            status=400)

        if not mirror.is_overtime():
            return Response(data={'error': _('The mirror is overtime')},
                            status=400)
        if not mirror.is_online():
            return Response(data={'error': _('Mirror is offline')},
                            status=400)

        if (mirror.lock_date != mirror.modify_date) and \
                (timezone.now() < (mirror.modify_date + timedelta(seconds=2))):
            return Response(data={'error': _('You have to wait for 2 seconds')})

        mirror.is_locked = True
        mirror.user = request.user
        mirror.save()

        visitor = request.user
        photo = Photo.objects.create(visitor=visitor, mirror=mirror)

        log.info('create photo id: {}'.format(photo.id))
        content = {'photo_id': photo.id}
        # SENDING A request for nitification to pusher service,
        # which will push the ANDROID APP.
        msg = 'New photo ({}) is created!'.format(photo.id)
        Notification.objects.create(message=msg, owner=visitor)
        # log.info('umeng json: {}, {}'.format(send_json, receive_info))
        return Response(data={'id': photo.id}, status=201)

    def list(self, request, *args, **kwargs):
        """
        Get all photo order by time (id) desc.
        Can be used for search (and it is used).
        q -- Search parameter.
        """
        qs = Photo.p_objects.select_related('original', 'visitor__visitor',
                                            'visitor__vendor__store',
                                            'group')
        qs = qs.filter(Q(group__is_private=False)) \
            .order_by('-photostamp__confidence').distinct()
        qs = self.filter_queryset(qs)

        return self.get_list_response(qs, serializers.PhotoListSerializer)

    @list_route(methods=['get'])
    def article_photos(self, request, *args, **kwargs):
        """
        get all photos included in articles
        """
        qs = Photo.p_objects.select_related('original', 'visitor__visitor',
                                            'visitor__vendor__store',
                                            'group')
        qs = qs.filter(article__isnull=False).distinct()
        qs = self.filter_queryset(qs)

        return self.get_list_response(qs, serializers.PhotoListSerializer)

    def partial_update(self, request, *args, **kwargs):
        """
        THIS REQUEST CALLED FROM ANDROID APP.
        Upload pictures url parameters plus time parameters also sign
        == + key time field value of md5 value.
        ---
        # YAML (must be separated by `---`)

        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: picture
              type: file
            - name: timestamp
              paramType: query
            #- name: id
            #  paramType: query
        """
        timestamp = request.data.get('timestamp', None)
        checksum = request.data.get('checksum', None)
        if not check_sign(timestamp, checksum):
            return Response(data={'error': _('Checksum error')})
        log.info('sign correct')
        pid = kwargs.get('pk', None)
        if not pid:
            return Response(data={'error': _('Missed argument  - pk')})

        # CLEAR THIS
        try:
            photo = Photo.objects.get(id=pid)
        except Photo.DoesNotExist:
            return Response(data={'error': _('Photo does not exist')})

        context = {'request': request}
        serializer = serializers.PhotoSerializer(instance=photo)

        return Response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        """ Because of clonning photo this handler does not delete photo.
         It is only unbinds from the group."""
        instance = self.get_object()
        if instance.photo and instance.photo.name:
            instance.group = None
            instance.save()
        else:
            instance.delete()
        return Response(status=204)

    @detail_route(methods=['patch'])
    def edit(self, request, *args, **kwargs):
        """ Manual update photo """
        # TODO: SET object permissions
        pid = kwargs.get('pk', None)
        try:
            photo = Photo.objects.get(id=pid)
        except Photo.DoesNotExist:
            return Response(data={'error': _('Photo does not exist')})

        visitor = request.user

        if visitor.pk != photo.visitor_id:
            return Response(data={'error': _('Only the owner can edit photo')})
        context = {'request': request}
        serializer = serializers.PhotoSerializer(instance=photo,
                                                 data=request.data,
                                                 partial=True, context=context)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @detail_route(methods=['get'])
    def like(self, request, *args, **kwargs):
        """ Handler that increments likes """
        obj = self.get_object()

        try:
            Like.objects.create(visitor_id=request.user.id, photo_id=obj.id)

            # Not using default object or queryset, to reduce the queryset
            like_count = Photo.objects.get(id=obj.id).like_set.count()

            # send notification to the owner
            msg = "{} likes your photo({})!" \
                .format(get_nickname(request.user), obj.title)
            Notification.objects.create(message=msg, owner=obj.visitor)
            data = {'like_count': like_count}
            status = 200
            # Like count is useless
        except IntegrityError:
            data = {'error': _('You have like it already!')}
            status = 400

        return Response(data, status)

    @detail_route(methods=['delete'], permission_classes=())
    def dislike(self, request, *args, **kwargs):
        """ Remove like from liked list. this handler does not
        require any special permission. Because it will throw exception
        if anything is  wrong. """
        obj = self.get_object()
        try:
            Like.objects.get(visitor_id=request.user.id, photo_id=obj.id) \
                .delete()
            # send notification to the owner
            msg = "{} does not like your photo({}) any more!" \
                .format(get_nickname(request.user), obj.title)
            Notification.objects.create(message=msg, owner=obj.visitor, type='warning')
            return Response(status=204)
        except Exception:
            raise ValidationError({'detail': _('You can dislike it.')})

    @list_route(methods=['get'])
    def newest(self, request, *args, **kwargs):
        """ Providing a list of the public groups newest photos """
        qs = Photo.a_objects.select_related('original', 'visitor__visitor',
                                            'visitor__vendor__store', 'group')
        qs = qs.filter(Q(group__is_private=False) &
                       ~Q(visitor_id=request.user.id)) \
            .order_by('-pk').distinct()

        return self.get_list_response(qs, serializers.PhotoListSerializer)

    @list_route(methods=['get'])
    def my_photos(self, request, *args, **kwargs):
        """ 
        Providing a list of photos in public groups that are not included
        in an article of current visitor
        """
        qs = Photo.a_objects.select_related('original', 'visitor__visitor',
                                            'visitor__vendor__store', 'group')
        qs = qs.filter(Q(article__isnull=True) &
                       Q(visitor_id=request.user.id)) \
            .order_by('-pk').distinct()

        return self.get_list_response(qs, serializers.PhotoListSerializer)

    @detail_route(methods=['post'])
    def clone(self, request, *args, **kwargs):
        """ Make a duplicate from existing photo record.
        Currently Swagger presents wrong scheme.
        group -- ID of the group where are you going to place cloned photo. """

        # TODO: optimize
        if 'group' not in request.data:
            raise ValidationError({'group': _('This parameter is required.')})

        obj = self.get_object()

        if obj.creator and obj.original:
            creator = obj.creator_id
            original = obj.original_id
        else:
            creator = obj.visitor_id
            original = obj.id

        title = obj.title if not request.data.get('title') \
            else request.data['title']

        description = obj.description if not request.data.get('description') \
            else request.data['description']

        # send notification to the owner
        msg = "{} saves your photo({})!" \
            .format(get_nickname(request.user), obj.title)
        Notification.objects.create(message=msg, owner=obj.visitor)

        data = {'original': original,
                'creator': creator,
                'visitor': request.user.pk,
                'group': request.data['group'],
                'title': title,
                'article': obj.article,
                'description': description}
        context = {'request': request}
        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)

    @list_route(methods=['get'])
    def liked_list(self, request, *args, **kwargs):
        """ Providing a photo list of liked photos. """
        qs = Photo.p_objects.select_related('original', 'visitor__visitor')
        qs = qs.filter(like__visitor_id=request.user.id)

        return self.get_list_response(qs, serializers.PhotoListSerializer)

    @detail_route(methods=['post'])
    def add_links(self, request, *args, **kwargs):
        """ Create a record in the Link table, which represents relation
        between photo and commodity.
            Params:
                commodities: list of commodities ids, required.
        This logic can be also implemented in the serializer.
        Bulk create not fits, because it can return ID.
        """
        if not hasattr(request.user, 'vendor'):
            raise PermissionDenied({'detail': _('You have not permission '
                                                'to perform this action')})

        # photo pk
        pk = self.get_object().pk
        context = {'request': request}

        link_limit = 3
        count = Link.objects.filter(photo_id=pk).count()
        if count >= link_limit:
            raise ValidationError(_('You can`t add more links.'))

        try:
            commodities = request.data['commodities']

            commodity_qs = Commodity.objects.filter(id__in=commodities)
            if any(i.store_id != request.user.id for i in commodity_qs):
                raise ValidationError({'detail': _('You can link only to '
                                                   'your own commodities ')})

            # not tested feature
            lim = link_limit - count
            sliced = commodities[:lim]
            response_data = []
            for n, i in enumerate(sliced):
                data = {'commodity': i, 'photo': pk}
                serializer = serializers.LinkSerializer(data=data,
                                                        context=context)
                serializer.is_valid(True)
                serializer.save()
                response_data.append(serializer.data)

        except KeyError as e:
            raise ValidationError({'error': _('{} parameter is required')
                                  .format(e.message)})
        except Exception as e:
            raise ValidationError({'error': e.message})

        return Response(response_data, 201)

    @detail_route(methods=['post'])
    def remove_link(self, request, *args, **kwargs):
        """ This handler is here to same permissions as this viewset has.
        Removes a commodity link from photo instance.
        It is important.
        link -- ID of the Link instance bound to the photo.
        """
        self.get_object()
        try:
            Link.objects.get(id=request.data['link']).delete()
            return Response(status=204)
        except KeyError as e:
            raise ValidationError({'error': _('{} parameter is required')
                                  .format(e.message)})

    @detail_route(methods=['get'])
    def similar(self, request, pk, *args, **kwargs):
        """
            Retreiving "similar" photo list.
            Flow:
                1. Select photo by ID.
                2. Select its stamps (tags) IDs. With help of Django M2M
                   we can directly call "stamps",
                   without previous calling "photostamp_set".
                3. Order fetched stamps by confidence of
                   the related photostamp.
                4. Make a list from that IDs and slice them,
                   we need only that which have confidence over 30.
                5. Make a query that fetches photos with chosen stamp IDS.
                6. Filter queryset with photostamps over 30.
            This view is not tested yet.
        """
        obj = self.get_object()
        if obj.original:
            obj = obj.original
        # TODO: optimize querysets
        mc = 25  # minimal confidence
        stamp_ids = obj.stamps.filter(photostamp__confidence__gte=mc) \
            .order_by('-pk') \
            .values_list('id', flat=True)

        qs = Photo.a_objects.select_related('original', 'visitor__visitor',
                                            'visitor__vendor__store',
                                            'group')
        qs = qs.filter(Q(group__is_private=False) &
                       ~Q(pk=pk) & Q(stamps__id__in=stamp_ids) &
                       Q(photostamp__confidence__gte=mc)) \
            .order_by('-pk').distinct()

        return self.get_list_response(qs, serializers.PhotoListSerializer)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author__visitor')
    serializer_class = serializers.CommentSerializer
    permission_classes = [IsVisitorOrVendor]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['author'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        photo = Photo.objects.get(id=int(data['photo']))
        # send notification to the owner
        msg = "{} gives a comment to your photo({})!" \
            .format(get_nickname(request.user), photo.title)
        Notification.objects.create(message=msg, owner=photo.visitor)

        return Response(serializer.data, status=201, headers=headers)

    @detail_route(methods=['get'])
    def like(self, request, *args, **kwargs):
        """ Handler that increments likes """
        obj = self.get_object()
        status = 400

        pk = kwargs['pk']
        try:
            isinstance(request.session['comment_ids'], list)
        except KeyError:
            self.request.session['comment_ids'] = []
        if pk in self.request.session['comment_ids']:
            data = {'error': _('You have liked that comment before.')}
        else:
            obj.like = F('like') + 1
            obj.save()
            self.request.session['comment_ids'] += [pk]
            data = {'like': self.get_object().like}
            status = 200
        return Response(data, status)


class TagViewSet(mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    # TODO: create actual permissions
    queryset = Tag.objects.select_related('group__owner', 'visitor__visitor')
    serializer_class = serializers.TagSerializer
    pagination_class = None
    permission_classes = [MemberCanServe]


class MemberViewSet(viewsets.ModelViewSet):
    """ Useless currently """
    queryset = Member.objects.select_related('group', 'visitor__visitor')
    serializer_class = serializers.MemberSerializer
    pagination_class = None
    permission_classes = []


class GroupViewSet(OwnerCreateMixin, viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrMember]
    filter_fields = ('owner',)

    # For update use only method patch

    def get_queryset(self):
        """ Pretty complex queryset for retreiving groups """
        visitor = self.request.user
        prefetch = Prefetch('photo_set',
                            queryset=Photo.objects.
                            select_related('original__group',
                                           'original__visitor', ))
        qs = Group.objects.select_related('owner__visitor'). \
            prefetch_related('tag_set', 'member_set',
                             'followgroup_set')
        qs = qs.prefetch_related(prefetch)
        if self.request.method == 'GET' and not self.kwargs.get('pk', None):

            qs = qs.filter(Q(is_private=False) | Q(owner=visitor) |
                           Q(member__visitor=visitor)).distinct()
        else:
            # TODO: optimize for detail view
            # TODO: something redundant with prefech related
            qs = qs.prefetch_related('member_set__visitor__visitor',
                                     'member_set__visitor__vendor__store')
        return qs

    def get_serializer_class(self):
        # SET up a serializer map
        if self.request.method == 'GET' and not self.kwargs.get('pk', None):
            return serializers.GroupListSerializer
        return serializers.GroupDetailSerializer

    def perform_create(self, serializer):
        group = serializer.save()
        members = self.request.data.get('members')
        if members:
            member_batch = (Member(group=group, visitor_id=i) for i in members)
            Member.objects.bulk_create(member_batch)

    @detail_route(methods=['post'])
    def photo_create(self, request, *args, **kwargs):
        """ Handler to save an uploaded photo to the 'group'.
         It is necessary to perform self.get_object to check permission. """

        data = request.data
        data['group'] = self.get_object().id
        data['visitor'] = self.request.user.id
        context = {'request': request}
        serializer = serializers.PhotoSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=201)

    @detail_route(methods=['get'])
    def photo_list(self, request, *args, **kwargs):
        """ Photo list for specified group """
        group = self.get_object()
        qs = Photo.p_objects.select_related('visitor__visitor',
                                            'visitor__vendor')
        qs = qs.filter(group=group)
        context = {'request': request}
        serializer_class = serializers.PhotoListSerializer
        # qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = serializer_class(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(qs, many=True, context=context)
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def snapshot(self, request, *args, **kwargs):
        """ Handler to save a photo taken from weixin JS API """
        raise NotImplementedError

    @detail_route(methods=['post'])
    def member_add(self, request, *args, **kwargs):
        """
        Add visitor to the group by username.
        It is necessary to perform self.get_object to check permission.
        username -- username of the collaborator to add.
         """
        pk = self.get_object().id
        status = 400
        context = {'request': request}
        try:
            username = request.data['username']
            visitor = Visitor.objects.get(user__username=username)
        except KeyError as e:
            data = {'error': _('{} parameter is required').format(e.message)}
        except Visitor.DoesNotExist:
            data = {'error': _('Matching user does not exists')}
        else:
            member_data = {'visitor': visitor.pk, 'group': pk}
            serializer = serializers.MemberSerializer(data=member_data,
                                                      context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = serializer.data
            status = 201
        return Response(data, status=status)

    @detail_route(methods=['post'])
    def member_vendor_add(self, request, *args, **kwargs):
        """
        Add visitor (VENDOR!) to the group by store`s brand name.
        It is necessary to perform self.get_object to check permission.
        Warning: it is not programmable restricted that members of the
        vendor(store) group can instances of the vendor.
        username -- username of the collaborator to add.
        """
        # TODO: implement restriction.

        pk = self.get_object().id
        status = 400
        context = {'request': request}
        try:
            # Argument left with name "username" to be compatible with frontend
            # I do not want to write a completely new frontend for store part.
            username = request.data['username']
            vendor = Vendor.objects.get(store__name=username)
        except KeyError as e:
            data = {'error': _('{} parameter is required').format(e.message)}
        except Vendor.DoesNotExist:
            data = {'error': _('Matching user does not exists')}
        else:
            member_data = {'visitor': vendor.pk, 'group': pk}
            serializer = serializers.MemberSerializer(data=member_data,
                                                      context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = serializer.data
            status = 201
        return Response(data, status=status)

    @detail_route(methods=['post'])
    def member_remove(self, request, *args, **kwargs):
        """ Remove member from group.
        member -- ID of the member (collaborator)
        """
        status = 400
        try:
            member_id = request.data['member']
            member = Member.objects.get(id=member_id, group=self.get_object())
        except KeyError as e:
            data = {'error': _('{} parameter is required').format(e.message)}
        except Member.DoesNotExist:
            data = {'error': _('Matching collaborator does not exists')}
        else:
            member.delete()
            data = None
            status = 204
        return Response(data, status=status)

    def member_email(self, request, *args, **kwargs):
        """ Invite visitor to the group by email """
        raise NotImplementedError

    def member_invite(self, request, *args, **kwargs):
        """ Add (handle) visitor`s invite to the group """
        raise NotImplementedError

    @detail_route(methods=['post'])
    def tag_create(self, request, *args, **kwargs):
        """ Add a group tag. It is here because of object permissions.
            It is necessary to perform self.get_object to check permission. """
        data = request.data
        data['group'] = self.get_object().id
        data['visitor'] = self.request.user.id

        serializer = serializers.TagSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=201)

    @list_route(methods=['get'])
    def visitor_list(self, request, *args, **kwargs):
        """ Representation of visitor list. Only visitors """
        status = 400
        context = {'request': request}

        try:
            q = request.query_params['q']
            qs = Visitor.objects.filter(~Q(pk=request.user.id) &
                                        Q(user__username__icontains=q))[:5]
            serializer = VisitorShortSerializer(qs, many=True, context=context)
            data = serializer.data
            status = 200
        except KeyError as e:
            data = {'error': _('{} parameter is required').format(e.message)}
        return Response(data=data, status=status)

    @list_route(methods=['get'])
    def vendor_list(self, request, *args, **kwargs):
        """ Representation of vendor list """
        status = 400
        context = {'request': request}
        try:
            q = request.query_params['q']
            qs = Vendor.objects.filter(~Q(pk=request.user.id) &
                                       Q(store__name__icontains=q))[:5]

            serializer = VendorStoreSerializer(qs, many=True, context=context)
            data = serializer.data
            status = 200
        except KeyError as e:
            data = {'error': _('{} parameter is required').format(e.message)}
        return Response(data=data, status=status)

    @list_route(methods=['get'])
    def my_groups(self, request, *args, **kwargs):

        visitor = self.request.user
        qs = Group.objects.select_related('owner__visitor')
        qs = qs.prefetch_related('tag_set')
        prefetch = Prefetch('photo_set',
                            queryset=Photo.p_objects.select_related('original'))
        qs = qs.prefetch_related(prefetch)
        qs = qs.filter(Q(owner=visitor) | Q(member__visitor=visitor)) \
            .distinct()
        serializer_class = self.get_serializer_class()
        page = self.paginate_queryset(qs)
        context = {'request': request}

        if page is not None:
            serializer = serializer_class(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(qs, many=True, context=context)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def my_groups_short(self, request, *args, **kwargs):
        visitor = self.request.user
        qs = Group.objects.all()
        qs = qs.filter(Q(owner=visitor) | Q(member__visitor=visitor)) \
            .distinct()
        serializer = serializers.GroupShortSerializer(qs, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def follow_groups(self, request, *args, **kwargs):
        """ Returns the groups which the customer is following """
        visitor = self.request.user
        qs = FollowGroup.objects.filter(follower=visitor)
        group_ids = [item.group.id for item in qs]
        qs = Group.objects.filter(id__in=group_ids)

        serializer_class = self.get_serializer_class()
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        context = {'request': request}
        serializer = serializer_class(qs, many=True, context=context)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def follow(self, request, *args, **kwargs):
        """ Follow the group by the customer """
        obj = self.get_object()

        if obj.owner == request.user:
            data = {'error': _('You cannot follow your group!')}
            status = 400
        elif FollowGroup.objects.filter(follower=request.user, group=obj):
            data = {'error': _('You have followed it already!')}
            status = 400
        else:
            FollowGroup.objects.create(follower=request.user, group=obj)
            follow_count = FollowGroup.objects.filter(group=obj).count()
            data = {'follow_count': follow_count}
            status = 200

            # send notification to the owner
            msg = "{} wants to follow your group({})!" \
                .format(get_nickname(request.user), obj.title)
            Notification.objects.create(message=msg, owner=obj.owner)

        return Response(data, status)

    @detail_route(methods=['get'])
    def unfollow(self, request, *args, **kwargs):
        """ Unfollow the group by the customer """
        obj = self.get_object()

        try:
            FollowGroup.objects.get(follower_id=request.user.id,
                                    group_id=obj.id).delete()

            follow_count = FollowGroup.objects.filter(group_id=obj.id).count()
            data = {'follow_count': follow_count}
            status = 200

            # send notification to the owner
            msg = "{} stops to follow your group({})!" \
                .format(get_nickname(request.user), obj.title)
            Notification.objects.create(message=msg, owner=obj.owner, type='warning')

        except IntegrityError:
            data = {'error': _('You have followed it already!')}
            status = 400

        return Response(data, status)


class GroupPhotoViewSet(mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """ Currently not used"""
    # TODO: delete
    queryset = Photo.objects.select_related('group', 'visitor__visitor')
    serializer_class = serializers.PhotoDetailSerializer
    pagination_class = None
    permission_classes = [MemberCanServe]


class VisitorViewSet(OwnerCreateMixin, viewsets.ModelViewSet):
    """ Follow and following logic"""
    queryset = FollowUser.objects.all()

    @list_route(methods=['get'])
    def follow_users(self, request, *args, **kwargs):
        """
        return users who the visitor follows
        """
        visitor = self.request.user
        qs_follow = FollowUser.objects.filter(follower=visitor)
        user_ids = [item.user.id for item in qs_follow]

        qs_visitor = Visitor.objects.filter(user__id__in=user_ids)
        qs_store = Store.objects.filter(vendor__user__id__in=user_ids)

        v_serializer = VisitorShortSerializer(qs_visitor, many=True)
        v_store = StoreShortSerializer(qs_store, many=True)

        data = v_serializer.data + v_store.data
        status = 200

        return Response(data={'results': data}, status=status)

    @list_route(methods=['get'])
    def followers(self, request, *args, **kwargs):
        """
        Returns followers for a user
        """
        visitor = self.request.user
        qs_follow = FollowUser.objects.filter(user=visitor)
        user_ids = [item.follower.id for item in qs_follow]

        qs_visitor = Visitor.objects.filter(user__id__in=user_ids)
        qs_store = Store.objects.filter(vendor__user__id__in=user_ids)

        v_serializer = VisitorShortSerializer(qs_visitor, many=True)
        v_store = StoreShortSerializer(qs_store, many=True)

        data = v_serializer.data + v_store.data
        status = 200
        return Response(data={'results': data}, status=status)

    @detail_route(methods=['get'])
    def follow_user(self, request, *args, **kwargs):
        """ Handler that increments follows """
        if request.user.id == int(kwargs['pk']):
            data = {'error': _('You cannot follow yourself!')}
            status = 400
            return Response(data, status)

        try:
            FollowUser.objects.create(follower_id=request.user.id,
                                      user_id=kwargs['pk'])
            follow_count = FollowUser.objects \
                .filter(user_id=kwargs['pk']).count()
            data = {'follow_count': follow_count}
            status = 200

            # send notification to the owner
            msg = "{} wants to follow you!" \
                .format(get_nickname(request.user))
            Notification.objects.create(message=msg, owner_id=int(kwargs['pk']))

        except IntegrityError:
            data = {'error': _('You have followed the user already!')}
            status = 400
        # TODO: more convinient
        return Response(data, status)

    @detail_route(methods=['get'])
    def unfollow_user(self, request, *args, **kwargs):
        """ Handler that decreases likes """
        try:
            FollowUser.objects.get(follower_id=request.user.id,
                                   user_id=kwargs['pk']).delete()
            follow_count = FollowUser.objects.filter(user_id=kwargs['pk']).count()
            data = {'follow_count': follow_count}
            status = 200

            # send notification to the owner
            msg = "{} stops to follow you!" \
                .format(get_nickname(request.user))
            Notification.objects.create(message=msg, owner_id=int(kwargs['pk']), type='warning')

        except IntegrityError:
            data = {'error': _('You have followed the user already!')}
            status = 400

        return Response(data, status)


class NotificationViewSet(OwnerCreateMixin, viewsets.ModelViewSet):
    """ Notification logic"""
    queryset = Notification.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        data = request.data
        Notification.objects.create(type=data['type'], message=data['message'],
                                    owner_id=int(data['user_id']))
        return Response('success', status=201)

    @detail_route(methods=['get'])
    def reply_notification(self, request, *args, **kwargs):
        # reply the user's notification
        instance = self.get_object()
        instance.status = 'read'
        instance.save()

        status = 200
        return Response(data='success', status=status)

    @list_route(methods=['get'])
    def me(self, request):
        # return the user's read notifications
        nfs = Notification.objects.filter(owner=request.user, status='read')
        s_nfs = serializers.NotificationSerializer(nfs, many=True)
        status = 200

        return Response(data=s_nfs.data, status=status)


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = ()

    @list_route(methods=['get'])
    def store_followers(self, request, **kwargs):
        """
        Get the list of number of users who follow your store per day in the month
        Return accumulated list.
        """
        year = int(kwargs['year'])
        month = int(kwargs['month'])
        last_day = get_last_day_of_month(year, month)

        data_sum = []
        follows_sum = 0
        for day in range(1, last_day + 1):
            date = datetime.date(year, month, day)
            follows = FollowUser.objects. \
                filter(follow_date__date=date, user=request.user).count()
            follows_sum = follows_sum + follows
            data_sum.append([day, follows_sum])

        status = 200
        # data_sum = [[1, 12 - month], [2, 13], [3, 20], [4, 28], [5, 28], [6, 32], [7, 36], [8, 41],
        #             [9, 41], [10, 42], [11, 45], [12, 51]]
        return Response(data_sum, status)

    @list_route(methods=['get'])
    def group_followers(self, request, **kwargs):
        """
        Get the list of number of users who follow each group per day in the month
        Return accumulated list.
        """
        year = int(kwargs['year'])
        month = int(kwargs['month'])
        last_day = get_last_day_of_month(year, month)

        data = {}
        groups = Group.objects.filter(owner=request.user)
        for group in groups:
            data_sum = []
            followers_sum = 0
            for day in range(1, last_day + 1):
                date = datetime.date(year, month, day)
                follows = FollowGroup.objects. \
                    filter(follow_date__date=date, group=group).count()
                followers_sum = followers_sum + follows
                data_sum.append([day, followers_sum])
            data[group.title] = data_sum

        status = 200
        # data = {'My Wardrobe': [[0, 12-month], [1, 6.5], [2, 12.5], [3, 7], [4, 9],
        #                         [5, 6], [6, 11], [7, 6.5], [8, 8], [9, 7], [10, 12]]}
        return Response(data, status)

    @list_route(methods=['get'])
    def photo_fans(self, request, **kwargs):
        """
        Get the list of number of users who like your each photo per day in the month
        Return accumulated list.
        """
        year = int(kwargs['year'])
        month = int(kwargs['month'])
        last_day = get_last_day_of_month(year, month)

        data = {}
        # filter by owner
        photos = Photo.objects.filter(visitor=request.user)
        for photo in photos:
            data_sum = []
            followers_sum = 0
            for day in range(1, last_day + 1):
                date = datetime.date(year, month, day)
                follows = Like.objects. \
                    filter(like_date__date=date, photo=photo).count()
                followers_sum = followers_sum + follows
                data_sum.append([day, followers_sum])
            title = photo.title or 'Untitled'
            data[title] = data_sum

        status = 200
        return Response(data, status)

    @list_route(methods=['get'])
    def photo_clones(self, request, **kwargs):
        """
        Get the list of number of photos who clone your each photo per day in the month
        Return accumulated list.
        """
        year = int(kwargs['year'])
        month = int(kwargs['month'])
        last_day = get_last_day_of_month(year, month)

        data = {}
        # filter by creator
        photos = Photo.objects.filter(creator=request.user)
        for photo in photos:
            data_sum = []
            followers_sum = 0
            for day in range(1, last_day + 1):
                date = datetime.date(year, month, day)
                follows = Photo.objects. \
                    filter(create_date__date=date, original=photo).count()
                followers_sum = followers_sum + follows
                data_sum.append([day, followers_sum])
            title = photo.title or 'Untitled'
            data[title] = data_sum

        status = 200
        return Response(data, status)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_signature(request):
    """
    **Context**
    This handler used for wechat js library purpose.
    For example for getting user location
    I need to set up a signature (on that page) before.
    """
    # TODO: replace file serving with redis
    # HOOK for ANGULARJS APP for wxlib purpose
    location = request.query_params.get('location', None)

    if not location:
        return Response(status=400)

    jsapi = JsApi_pub()
    filename = '/tmp/mirrors_weixin_status'
    data = None
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = pickle.load(f)
    if data and data['time'] + timedelta(seconds=7200) >= timezone.now():
        ticket = data['ticket']
    else:
        client_access_token_info = json.loads(jsapi.get_access_tocken())
        client_access_token = client_access_token_info['access_token']
        ticket_info = jsapi.get_jsapi_ticket(client_access_token)
        ticket = json.loads(ticket_info)['ticket']

        with open(filename, 'w+') as f:
            ticket_info = {'ticket': ticket, 'time': timezone.now()}
            f.truncate()
            pickle.dump(ticket_info, f)

    url, frag = urldefrag(location)

    js_info = jsapi.get_signature(url=url, ticket=ticket)
    return Response(data=js_info)
