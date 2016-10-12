from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

snapshot_router = DefaultRouter()

snapshot_router.register(r'article', views.ArticleViewSet, 'article')
snapshot_router.register(r'mirror', views.MirrorViewSet, 'mirror')
snapshot_router.register(r'photo', views.PhotoViewSet, 'photo')
snapshot_router.register(r'comment', views.CommentViewSet, 'comment')
snapshot_router.register(r'tag', views.TagViewSet, 'tag')
snapshot_router.register(r'member', views.MemberViewSet, 'member')
snapshot_router.register(r'group', views.GroupViewSet, 'group')
snapshot_router.register(r'group-photo', views.GroupPhotoViewSet,
                         'photo-g')
snapshot_router.register(r'visitor', views.VisitorViewSet, 'visitor')
snapshot_router.register(r'notification', views.NotificationViewSet,
                         'notification')
snapshot_router.register(r'dashboard/(?P<year>\d{4})/(?P<month>\d{,2})',
                         views.AnalyticsViewSet, 'dashboard')

urlpatterns = [
    url(r'^signature/$', views.get_signature, name='signature'),
]

urlpatterns += snapshot_router.urls
