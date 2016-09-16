"""businesscenter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from vendor_admin.admin import site
from snapshot import views

urlpatterns = [
    # temporary
    url(r'^$', views.index, name='index'),
    url(r'^store/', TemplateView.as_view(template_name='store.html'),
        name='store'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/django-rq/', include('django_rq.urls')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^business_center/', site.urls),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^account/', include('account.urls', namespace='account')),
    url(r'^catalog/', include('catalog.urls', namespace='catalog')),
    url(r'^visitor/', include('visitor.urls', namespace='visitor')),
    url(r'^api/v1/', include('snapshot.urls', namespace='snapshot')),

]


if settings.DEBUG:
    if settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
    if settings.STATIC_ROOT:
        urlpatterns += static(settings.STATIC_URL,
                              document_root=settings.STATIC_ROOT)
