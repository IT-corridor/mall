from __future__ import unicode_literals

from rest_framework import permissions


class IsVendorSimple(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        base_perm = super(IsVendorSimple, self).has_permission(request, view)
        if base_perm:
            if hasattr(request.user, 'vendor'):
                return True
        return request.user.is_staff
