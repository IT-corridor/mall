# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import random
from urllib import quote_plus
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate, \
    update_session_auth_hash
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, list_route
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .serializers import VisitorSerializer, VisitorExtraSerializer, \
    VisitorCreateSerializer, VisitorProfileSerializer, VisitorLoginSerializer, \
    PhoneSerializer, CodeSerializer
from .oauth2 import WeixinBackend, WeixinQRBackend
from .models import Visitor, VisitorExtra
from .permissions import IsVisitorSimple, IsVisitorOrReadOnly
from .extra_handlers import PendingUserVault, PhonesVault
from .sms import TaoSMSAPI
from utils.serializers import UserPasswordSerializer, UserSetPasswordSerializer
from snapshot.models import Notification
from vutils.notification import trigger_notification


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_view(request):
    # USE openid
    status = 400
    backend = 'weixin'
    try:
        extra = VisitorExtra.objects.get(openid=request.data['weixin'],
                                         backend=backend)
        serializer = VisitorSerializer(instance=extra.weixin.visitor)
        user_data = serializer.data
        user = authenticate(weixin=extra.openid)
        login(request, user)
    except KeyError as e:
        user_data = {'weixin': _('Missed param')}
    except Visitor.DoesNotExist:
        user_data = {'weixin': _('User does not exists')}
    except Exception as e:
        user_data = {'error': e.message}
    else:
        status = 200
    return Response(user_data, status=status)


@api_view(['GET'])
@permission_classes((AllowAny,))
def is_authenticated(request):
    if request.user.is_authenticated() \
            and hasattr(request.user, 'visitor'):
        r = True
    else:
        r = False
    return Response({'is_authenticated': r})


@api_view(['GET'])
@permission_classes((AllowAny,))
def logout_view(request):
    logout(request)
    return Response(status=200)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def verify_captcha(request, captcha_key, captcha_value):
    """ PIN VERIFICATION. NO USE FOR NOW """
    # THAT LOGIC LOOKS STUPID. But I leave it for now.
    data = {}
    status = 400
    if not captcha_value:
        data = {'captcha': _('Verification code required')}
    else:
        server_captcha = request.session.get(captcha_key)
        if server_captcha != captcha_value:
            data = {'captcha_error': _('Code is incorrect or has expired')}
        else:
            del request.session[captcha_key]
            status = 200

    return Response(data, status=status)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def dummy_api(request):
    return Response(data={'message': 'Hello'}, status=200)


def index(request):
    """ OAuth2 auhentication with Weixin (Wechat).
        Params:
            qr: if it has some value that can be interpreted like True,
                then we use qr code for authentication.
                Required for the desktop clients.
    """
    url = request.GET.get("qr", "1")
    weixin_oauth2 = WeixinBackend()
    redirect_url = '{}://{}{}'.format(request.scheme,
                                      request.get_host(),
                                      reverse('visitor:openid'))
    redirect_url += '?url={}'.format(url)
    #mail_admins('redirect is', redirect_url)
    redirect_url = 'http://www.atyichu.com/visitor/openid'
    #mail_admins('actual redirect is', redirect_url)
    url = weixin_oauth2.get_authorize_uri(redirect_url)
    return HttpResponseRedirect(url)


def openid(request):
    """ OAuth2 handler for weixin """
    # TODO: RESOLVE WITH CORS!!!
    redirect = 'http://www.atyichu.com'
    qr = request.GET.get("qr", None)
    response = HttpResponseRedirect(redirect + '#!/')

    if request.user.is_authenticated():
        return response

    code = request.GET.get("code", None)

    if not code:
        return JsonResponse({'error': _('You don`t have weixin code.')})

    if qr:
        weixin_oauth = WeixinQRBackend()
        backend = 'weixin_qr'
    else:
        weixin_oauth = WeixinBackend()
        backend = 'weixin'
    try:
        token_data = weixin_oauth.get_access_token(code)
    except TypeError:
        return JsonResponse({'error': _('You got error trying to get openid')})

    user_info = weixin_oauth.get_user_info(token_data['access_token'],
                                           token_data['openid'])
    data = {'avatar_url': user_info.get('headimgurl'),
            'nickname': user_info.get('nickname'),
            'unionid': token_data['unionid'],
            'extra': {
                'openid': token_data['openid'],
                'access_token': token_data['access_token'],
                'expires_in': token_data['expires_in'],
                'refresh_token': token_data['refresh_token'],
                'backend': backend,
            }
            }

    try:
        extra = VisitorExtra.objects.get(openid=token_data['openid'],
                                         backend=backend)
        s = VisitorExtraSerializer(instance=extra, data=data['extra'],
                                   partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        visitor = extra.weixin.visitor
        # Remove after WIPE
        visitor_data = {'nickname': data['nickname'],
                        'unionid': data['unionid']}

        visitor_s = VisitorSerializer(instance=visitor, data=visitor_data,
                                      partial=True)
        visitor_s.is_valid(raise_exception=True)
        visitor = visitor_s.save()
    except VisitorExtra.DoesNotExist:
        serializer = VisitorSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        visitor = serializer.save()
        extra = None

    if not extra:
        extra = visitor.weixin.visitorextra_set.get(backend=backend)
    user = authenticate(weixin=extra.openid, backend=backend)
    login(request, user)
    return response


@api_view(['POST'])
@permission_classes((AllowAny,))
def openid_api(request):
    """ To continue authentication via Wecha / weixin you need pass a code
    code -- A code from wexin (to obtain access_token).
    So you need a code.
    Important to use same API KEY and SECRET as We use at django app.
    :return: visitor data.
    """
    if request.user.is_authenticated():
        return Response({'error': _('Already authenticated.')}, 400)

    code = request.data.get("code", None)

    if not code:
        return Response({'error': _('You don`t have weixin code.')}, 400)

    weixin_oauth = WeixinBackend()
    backend = 'weixin'
    try:
        token_data = weixin_oauth.get_access_token(code)
    except TypeError:
        return Response({'error': _('You got error trying to get openid')},
                        400)

    user_info = weixin_oauth.get_user_info(token_data['access_token'],
                                           token_data['openid'])
    data = {'avatar_url': user_info.get('headimgurl'),
            'nickname': user_info.get('nickname'),
            'unionid': token_data['unionid'],
            'extra': {
                'openid': token_data['openid'],
                'access_token': token_data['access_token'],
                'expires_in': token_data['expires_in'],
                'refresh_token': token_data['refresh_token'],
                'backend': backend,
            }
    }

    context = {'request': request}

    try:
        extra = VisitorExtra.objects.get(openid=token_data['openid'],
                                         backend=backend)
        s = VisitorExtraSerializer(instance=extra, data=data['extra'],
                                   partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        visitor = extra.weixin.visitor
        # Remove after WIPE
        visitor_data = {'nickname': data['nickname'],
                        'unionid': data['unionid']}

        visitor_s = VisitorSerializer(instance=visitor, data=visitor_data,
                                      partial=True, context=context)
        visitor_s.is_valid(raise_exception=True)
        visitor = visitor_s.save()
    except VisitorExtra.DoesNotExist:
        visitor_s = VisitorSerializer(data=data, context=context)
        visitor_s.is_valid(raise_exception=True)
        visitor = visitor_s.save()
        extra = None

    if not extra:
        extra = visitor.weixin.visitorextra_set.get(backend=backend)
    user = authenticate(weixin=extra.openid, backend=backend)
    login(request, user)

    return Response(visitor_s.data)


@api_view(['POST'])
@permission_classes((IsVisitorSimple,))
def update_visitor(request):
    """ Updating user data from weixin. Sync.
    Only for authenticated wechat visitor """
    # TODO: TEST
    qr = request.data.get('qr', None)
    if qr:
        wx = WeixinQRBackend()
        backend = 'weixin_qr'
    else:
        wx = WeixinBackend()
        backend = 'weixin'
    visitor = request.user.visitor
    extra = VisitorExtra.objects.get(weixin=visitor.weixin, backend=backend)
    data = {'access_token': extra.access_token,
            'openid': extra.openid}
    if extra.is_expired():
        data.update(wx.refresh_user_credentials(extra.refresh_token))
        s = VisitorExtraSerializer(instance=extra, data=data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
    user_info = wx.get_user_info(data['access_token'], data['openid'])
    user_data = {
        'avatar_url': user_info.get('headimgurl'),
        'nickname': user_info.get('nickname'),
    }
    context = {'request': request}
    serializer = VisitorSerializer(instance=visitor, data=user_data,
                                   partial=True, context=context)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data=serializer.data)


@api_view(['GET'])
@permission_classes((IsVisitorSimple,))
def get_me(request):
    """ Provides personal user data, username and thumb """
    visitor = request.user.visitor
    context = {'request': request}
    serializer = VisitorSerializer(instance=visitor, context=context)
    check_unread_notification(request.user)

    return Response(data=serializer.data)


def test_auth(request):
    host = request.get_host()
    if host == '127.0.0.1:8000':
        redirect_to = '127.0.0.1:8001' if request.GET.get('store') \
            else '127.0.0.1:8002'
        extra = VisitorExtra.objects.get(backend='weixin', openid='weixin')
        user = authenticate(weixin=extra.openid)
        login(request, user)
        response = HttpResponseRedirect(redirect_to)
        return response
    raise PermissionDenied


class ProfileViewSet(viewsets.GenericViewSet):
    """
    A simple ViewSet for listing or retrieving visitors.
    """
    permission_classes = (IsVisitorOrReadOnly,)

    def get_serializer_class(self):
        serializer_map = {
            'retrieve': VisitorProfileSerializer,
            'create': VisitorCreateSerializer,
            'edit': VisitorProfileSerializer,
            'change_password': UserPasswordSerializer,
            'login': VisitorLoginSerializer,
            'login_start': VisitorLoginSerializer,
            'login_end': VisitorLoginSerializer,
            'me': VisitorProfileSerializer,
            'send_code': PhoneSerializer,
            'verify_code': CodeSerializer,
            'wechat_phone': VisitorProfileSerializer,
            'reset_password': UserSetPasswordSerializer,
        }
        return serializer_map[self.action]

    def get_queryset(self):
        return Visitor.objects.all()

    def retrieve(self, request, pk=None):
        """ retreive visitor information, may be useless. """
        queryset = self.get_queryset()
        context = {'request': request}
        visitor = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(visitor, context=context)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def me(self, request):
        """ Retrieve information about own profile (visitor).
        Works only for authenticated user."""
        queryset = self.get_queryset()
        context = {'request': request}
        visitor = get_object_or_404(queryset, pk=request.user.id)
        serializer = self.get_serializer(visitor, context=context)
        return Response(serializer.data)

    def create(self, request):
        """ Create user. Redirect to get_me.
        SIGN UP: Step 3
        Important: this handler will take phone value only from cache.
        """
        data = request.data
        sessionid = request.session.session_key
        phones_vault = PhonesVault()
        data['phone'] = phones_vault.get_verify_by_sessionid(sessionid)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        visitor = serializer.save()
        user = authenticate(phone=visitor.phone,
                            password=data['password'])
        login(request, user)
        url = reverse('visitor:me')
        return HttpResponseRedirect(url)

    @list_route(methods=['patch'])
    def edit(self, request):
        """ PK not suplied visitor instance takes from request.user."""
        user = request.user
        # maybe following line is redundant
        self.check_object_permissions(request, user.visitor)
        if not user.visitor.phone and request.data.get('phone'):
            raise ValidationError({'phone':
                                       _('You can`t change phone '
                                         'before you bind it')})
        context = {'request': request}
        serializer = self.get_serializer(instance=user.visitor,
                                         data=request.data,
                                         partial=True, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @list_route(methods=['post'])
    def change_password(self, request):
        """ Change user`s password. PK not supplied."""
        user = request.user
        self.check_object_permissions(request, user.visitor)
        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        update_session_auth_hash(request, user)
        return Response(status=204)

    @list_route(methods=['post'])
    def login(self, request):
        """
        Simple login handler without any special checking.
        Handles login visitor by phone number
        """
        # TODO: Add verification code handling
        status = 400
        s = self.get_serializer(data=self.request.data)
        s.is_valid(raise_exception=True)
        context = {'request': request}
        try:
            user = authenticate(phone=s.data['phone'],
                                password=s.data['password'])
            serializer = VisitorSerializer(instance=user.visitor,
                                           context=context)
            data = serializer.data
            login(request, user)
        except Exception as e:
            data = {'error': e.message}
        else:
            status = 200
        return Response(data, status=status)

    @list_route(methods=['post'])
    def login_start(self, request):
        """
        Signing in with sms verification (2 factor auth)
        Handles login visitor by phone number.
        Works only with chinese phones.
        Can`t be tested from swagger.
        Currently not used.
        """
        # TODO: Add verification code handling
        status = 400
        s = self.get_serializer(data=self.request.data)
        s.is_valid(raise_exception=True)
        try:
            user = authenticate(phone=s.data['phone'],
                                password=s.data['password'])
            # create a session key manually, because django does not create
            #  a session for anonymous user
            pending_store = PendingUserVault()
            code = pending_store.add_by_sessionid(request, user)
            phone = s.data['phone']
        except Exception as e:
            data = {'error': e.message}
        else:
            sms_api = TaoSMSAPI(settings.TAO_SMS_KEY, settings.TAO_SMS_SECRET)
            r = sms_api.send_code(phone, code)
            if r:
                status = 200
                data = {'status': 'sent'}
            else:
                raise ValidationError({'code': [_('Code has not been sent.')]})
        return Response(data, status=status)

    @list_route(methods=['post'])
    def login_end(self, request):
        """ Verification code is required. """
        try:
            code = request.data['code']
            sessionid = request.session.session_key

            pending_store = PendingUserVault()
            user = pending_store.get_by_sessionid(sessionid, code)
            if user is None:
                raise ValidationError({'detail': [_('Code not sent.')]})
        except KeyError:
            raise ValidationError({'detail':
                                       _('Verification code is required!')})
        else:
            login(request, user)
            url = reverse('visitor:me')
            return HttpResponseRedirect(url)

    @list_route(methods=['post'])
    def send_code(self, request):
        """ Sending code to the phone. Required for the SIGN UP.
        SIGN UP: Step 1
         Optional request.data parameter -- is_exists.
         If this parameter sent with request,
         with value that can be interpreted as true.
         We assume that it phone should be existed, in any other case,
         we assume that this is a new phone and we should not have
         related record with it.
        """
        is_exists = request.data.pop('is_exists', False)
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.data['phone']

        if not is_exists and Visitor.objects.filter(phone=phone).exists():
            raise ValidationError({'phone':
                                       [_('This phone is registered.')]})

        if is_exists and not Visitor.objects.filter(phone=phone).exists():
            raise ValidationError({'phone':
                                       [_('This phone is not registered.')]})
        phones_vault = PhonesVault()
        code = phones_vault.add_by_sessionid(request, phone)
        sms_api = TaoSMSAPI(settings.TAO_SMS_KEY, settings.TAO_SMS_SECRET)
        r = sms_api.send_code(phone, code)
        if r:
            data = {'status': 'sent'}
            return Response(data, 200)
        else:
            raise ValidationError({'detail': [_('Code has not been sent.')]})

    @list_route(methods=['post'])
    def verify_code(self, request):
        """ Verifying sms code. Required for the SIGN UP.
        SIGN UP: Step 2 """
        serializer = CodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.data['code']
        sessionid = request.session.session_key
        phones_vault = PhonesVault()
        phone = phones_vault.get_pending_by_sessionid(sessionid, code)
        if phone is None:
            raise ValidationError({'code': [_('Code is wrong or outdated.')]})

        data = {'status': 'verified'}
        return Response(data, 200)

    @list_route(methods=['post'])
    def wechat_phone(self, request):
        """Sets the password and phone for existing weixin visitor.
         LOGIC: user can set password after he will verify his phone.
         If user has no phone, then user has no password.
         This handler uses 2 serializers. UserSetPasswordSerializer and
         VisitorProfileSerializer.

         Requires sms verification ( send_code and
        verify_code must be performed before).
         """

        user = request.user
        visitor = user.visitor
        if visitor.phone and user.password:
            raise ValidationError({'detail':
                                       [_('You already have a password.')]})
        sessionid = request.session.session_key
        phones_vault = PhonesVault()
        phone = phones_vault.get_verify_by_sessionid(sessionid)
        if phone is None:
            raise ValidationError({'code': [_('Can`t find your phone.')]})

        data = request.data
        s = UserSetPasswordSerializer(instance=user,
                                      data=data, partial=True)
        s.is_valid(raise_exception=True)
        user = s.save()

        update_session_auth_hash(request, user)

        serializer = self.get_serializer(instance=visitor,
                                         data={'phone': phone}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @list_route(methods=['post'])
    def reset_password(self, request):
        """ Handler that sets a new password to user identified by his phone.
        Requires sms verification ( send_code and
        verify_code must be performed before).

        """
        sessionid = request.session.session_key
        phones_vault = PhonesVault()
        phone = phones_vault.get_verify_by_sessionid(sessionid)
        if phone is None:
            raise ValidationError({'code': [_('Can`t find your phone.')]})

        visitor = Visitor.objects.get(phone=phone)
        user = visitor.user

        serializer = UserSetPasswordSerializer(instance=user,
                                               data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(status=204)


def check_unread_notification(user):
    """
    resend unread notifications for the user
    """
    for nf in Notification.objects.filter(owner=user, status='new'):
        trigger_notification('nf_channel_{}'.format(user.id),
                             'new_notification',
                             nf.message, nf.type, nf.id, nf.create_date)
