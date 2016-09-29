from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from . import views

profile_router = DefaultRouter()

profile_router.register(r'profile', views.ProfileViewSet, 'profile')
profile_router.register(r'chat', views.QuickbloxViewSet, 'chat')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^openid$', views.openid, name='openid'),
    url(r'^openid_api$', views.openid_api, name='openid_api'),
    url(r'^dummy/$', views.dummy_api, name='dummy'),
    url(r'^is_authenticated/$', views.is_authenticated, name='is_auth'),
    url(r'^me/$', views.get_me, name='me'),
    url(r'^test_auth/$', views.test_auth, name='test_auth'),
    url(r'^update/$', views.update_visitor, name='update'),
]

urlpatterns += profile_router.urls
