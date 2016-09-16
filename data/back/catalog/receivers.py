from __future__ import unicode_literals

from django.contrib.auth.models import Group, Permission


def add_vendor_catalog_perms(sender, **kwargs):
    group = Group.objects.get(name='vendors')
    permissions = Permission.objects. \
        filter(content_type__app_label__iexact='catalog')

    group.permissions.add(*permissions)
