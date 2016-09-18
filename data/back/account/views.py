from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.contrib.auth import logout, authenticate, login
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError
from . import serializers, models
from .permissions import IsVendorSimple
from catalog import serializers as cat_srlzrs
from catalog import models as cat_models
from utils import permissions
from utils.views import OwnerCreateMixin, OwnerUpdateMixin, PaginationMixin


class StoreViewSet(OwnerCreateMixin,
                   OwnerUpdateMixin,
                   PaginationMixin,
                   viewsets.ModelViewSet):
    """ Please assume that store primary key
        equals vendor primary key that equals user primary key.
        Vendor instance inherits PK from django user instance and
        Store instance inherits this PK from Vendor instance.
        KEEP IN MIND THIS PLEASE.
    """
    serializer_class = serializers.StoreSerializer
    permission_classes = (permissions.IsStoreOwnerOrReadOnly, )
    user_kwd = 'vendor'

    def get_queryset(self):
        return models.Store.objects.select_related('district__city__state')

    @list_route(methods=['get'])
    def my_store(self, request, *args, **kwargs):
        """ Retrieve vendor`s store, without specifying a pk value."""
        obj = self.get_object_by_owner_or_404()
        serializer = self.serializer_class(instance=obj,
                                           context={'request': request})
        return Response(data=serializer.data)

    @detail_route(methods=['patch'])
    def update_photo(self, request, *args, **kwargs):
        """ Used to update only the logo of the store.
        Nothing more guarantied."""
        if 'photo' not in request.data:
            raise ValidationError({'photo': _('This parameter is required.')})
        obj = self.get_object()
        context = {'request': request}
        serializer = self.serializer_class(instance=obj, data=request.data,
                                           partial=True, context=context)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @detail_route(methods=['patch'])
    def update_post(self, request, *args, **kwargs):
        """
        Update the post of the store.
        """
        if 'post' not in request.data:
            raise ValidationError({'post': _('This parameter is required.')})
        obj = self.get_object()
        serializer = self.serializer_class(instance=obj, data=request.data,
                                           partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @list_route(methods=['get'])
    def my_brands(self, request, *args, **kwargs):
        """ Presents a brand list that created by vendor fo the store.
            Used for simple list presentation and
            it is not requires pagination.
        """
        return self.get_response_by_owner(cat_models.Brand.objects.all(),
                                          cat_srlzrs.BrandSerializer)

    @list_route(methods=['get'])
    def my_commodities(self, request, *args, **kwargs):
        """ Presents a commodity list that created by vendor for the store.
            Uses pagination.
        """
        obj = self.get_object_by_owner_or_404()
        select = cat_models.Commodity.objects.filter(store=obj)\
            .select_related('brand', 'kind__category',)

        select = select.prefetch_related('colors', 'sizes')

        return self.get_list_response(select,
                                      cat_srlzrs.CommodityListVerboseSerializer)

    @detail_route(methods=['get'])
    def commodities(self, request, *args, **kwargs):
        """ Presents a commodity list that belongs to the store.
            Uses pagination.
        """
        obj = self.get_object()
        select = cat_models.Commodity.objects.filter(store=obj) \
            .select_related('brand', 'kind__category', 'color', 'size')

        return self.get_list_response(select,
                                      cat_srlzrs.CommodityListVerboseSerializer)

    @detail_route(methods=['get'])
    def overview(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {'request': request}
        serializer = serializers.StorePhotoSerializer(instance,
                                                      context=context)
        return Response(serializer.data)

    def get_response_by_owner(self, queryset, serializer_class):
        """ Shortcut to perform response based on owner`s queryset"""
        obj = self.get_object_by_owner_or_404()
        select = queryset.filter(store=obj)
        serializer = serializer_class(instance=select, many=True)
        return Response(serializer.data)

    def get_object_by_owner_or_404(self):
        """ Get the object store that belongs to the vendor
        (current authenticated user). Later can be extended."""
        user = self.request.user.id
        return get_object_or_404(self.get_queryset(), vendor=user)


class AbsListView(generics.ListAPIView):
    pagination_class = None

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super(AbsListView, self).get(request, *args, **kwargs)
        else:
            return Response({'detail': _('FORBIDDEN')}, status=403)


class StateView(AbsListView):

    queryset = models.State.objects.all()
    serializer_class = serializers.StateSerializer


class CityView(AbsListView):

    queryset = models.City.objects.select_related('state')
    serializer_class = serializers.CitySerializer


class District(AbsListView):

    queryset = models.District.objects.select_related('city__state')
    serializer_class = serializers.DistrictSerializer


class UserMixin:
    queryset = models.User.objects.\
        select_related('vendor__store__district__city__state')
    permission_classes = (permissions.IsUserOrReadOnly,)


class ProfileListCreateView(UserMixin, generics.ListCreateAPIView):
    """ READ Python MRO """
    serializer_class = serializers.UserCreateSerializer


class ProfileRetrieveUpdateView(UserMixin, generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UserUpdateSerializer


class ProfilePasswordUpdatedView(UserMixin, generics.UpdateAPIView):
    serializer_class = serializers.UserPasswordSerializer


@api_view(['GET'])
@permission_classes(())
def logout_view(request):
    logout(request)
    return Response({'logout': True}, status=200)


@api_view(['POST'])
@permission_classes(())
def login_view(request):
    data = {}
    status = 401
    try:
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)

        if hasattr(user, 'vendor'):
            vendor = user.vendor
            context = {'request': request}
            serializer = serializers.VendorBriefSerializer(instance=vendor,
                                                           context=context)
            data.update(serializer.data)
            status = 200
            login(request, user)
    except KeyError as e:
        # missing parameter
        data.update({'error': _('Missed parameter {}').format(e)})
        status = 400
    except AttributeError:
        # Unauthenticated user
        data.update({'error': _('Invalid combination of username and password')})

    return Response(data, status=status)


@api_view(['GET'])
@permission_classes((IsVendorSimple,))
def get_my_vendor(request):
    """ Provides personal vendor data, username and thumb """
    # TODO: Optimize queryset
    vendor = request.user.vendor
    context = {'request': request}
    serializer = serializers.VendorBriefSerializer(instance=vendor,
                                                   context=context)
    return Response(data=serializer.data)


@api_view(['GET'])
@permission_classes([])
def is_authenticated(request):
    if request.user.is_authenticated() \
            and hasattr(request.user, 'vendor'):
        r = True
    else:
        r = False
    return Response({'is_authenticated': r})
