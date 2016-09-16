from __future__ import unicode_literals

from django.contrib.auth.models import Group, Permission


def add_to_vendor_group(sender, instance=None, created=False, **kwargs):
    if created:
        instance.user.groups.add(Group.objects.get(name='vendors'))


def create_vendor_group(sender, **kwargs):
    group, _ = Group.objects.get_or_create(name='vendors')
    permissions = Permission.objects. \
        filter(content_type__model__iexact='store')

    group.permissions.set(permissions)
