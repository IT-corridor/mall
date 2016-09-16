from __future__ import unicode_literals

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class IsUserOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff or obj == request.user


class IsStoreOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(request.user, 'vendor') or hasattr(request.user, 'visitor'):
            return True

        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(request.user, 'vendor'):
            return request.user.id == obj.vendor_id

        return request.user.is_staff


class IsOwnerOrReadOnly(IsStoreOwnerOrReadOnly):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(request.user, 'vendor'):
            return request.user.id == obj.store_id

        return request.user.is_staff
