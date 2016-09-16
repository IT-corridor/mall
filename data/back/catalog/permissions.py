from __future__ import unicode_literals

from rest_framework import permissions

from utils.permissions import IsStoreOwnerOrReadOnly


class IsCommodityNestedOwnerOrReadOnly(IsStoreOwnerOrReadOnly):
    """ This permissions ONLY for GalleryViewSet."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(request.user, 'vendor'):
            return request.user.id == obj.commodity.store_id

        return request.user.is_staff
