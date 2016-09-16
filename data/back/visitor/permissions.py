from __future__ import unicode_literals

from rest_framework import permissions


class IsVisitor(permissions.IsAuthenticated):
    """Left as legacy """
    def has_permission(self, request, view):
        if view.action == 'create':
            # Allow any user to create mirror instances
            return True
        base_perm = super(IsVisitor, self).has_permission(request, view)
        if base_perm:
            if hasattr(request.user, 'visitor'):
                return True
        return request.user.is_staff


class IsVisitorOrVendor(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        if view.action == 'create':
            # Allow any user to create mirror instances
            return True
        base_perm = super(IsVisitorOrVendor, self)\
            .has_permission(request, view)
        if base_perm:
            if hasattr(request.user, 'visitor') or \
                    hasattr(request.user, 'vendor'):
                return True
        return request.user.is_staff


class IsVisitorSimple(permissions.IsAuthenticated):
    """ For weixin user"""
    def has_permission(self, request, view):
        base_perm = super(IsVisitorSimple, self).has_permission(request, view)
        if base_perm:
            if hasattr(request.user, 'visitor'):
                # if hasattr(request.user.visitor, 'weixin'):
                return True
        return request.user.is_staff


class IsVisitorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'visitor'):
            if obj.pk == request.user.pk:
                return True

        return request.user.is_staff
