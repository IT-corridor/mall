from __future__ import unicode_literals

from django.conf.urls import url
from django.views.decorators.cache import cache_page
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.routers import DefaultRouter


store_router = DefaultRouter()
store_router.register(r'stores', views.StoreViewSet, 'store')


urlpatterns = (
    url(r'^states/$', cache_page(300)(views.StateView.as_view()),
        name='state-list'),
    url(r'^cities/$', cache_page(300)(views.CityView.as_view()),
        name='city-list'),
    url(r'^districts/$', cache_page(300)(views.District.as_view()),
        name='district-list'),
    url(r'^vendors/$', views.ProfileListCreateView.as_view(),
        name='profile-list'),
    url(r'^vendors/(?P<pk>\d+)/$',
        views.ProfileRetrieveUpdateView.as_view(), name='profile-detail'),
    url(r'^vendors/(?P<pk>\d+)/password/$',
        views.ProfilePasswordUpdatedView.as_view(), name='profile-password'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^my_vendor/$', views.get_my_vendor, name='my_vendor'),
    url(r'^is_authenticated/$', views.is_authenticated, name='is_authenticated'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += store_router.urls

