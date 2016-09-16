from __future__ import unicode_literals

from rest_framework import permissions


class VisitorBasic(permissions.IsAuthenticated):
    """ Visitor (wechat)  and Vendor (store) are nested models
    from default django auth User model. Only their instances
    can take this permission."""
    def has_permission(self, request, view):
        base_perm = super(VisitorBasic, self).has_permission(request, view)
        if base_perm:
            if hasattr(request.user, 'visitor') or \
                    hasattr(request.user, 'vendor'):
                return True
        return request.user.is_staff


class IsOwnerOrMember(VisitorBasic):
    """ Only for GroupViewSet! """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and not obj.is_private:
            return True

        user = request.user
        if user.id == obj.owner_id:
            return True

        is_member = obj.member_set.filter(visitor_id=user.id).exists()

        if request.method == 'GET' and is_member:
            return True

        if request.method == 'POST' and is_member and\
                view.action in ['photo_create', 'tag_create']:
            return True

        return request.user.is_staff


class MemberCanServe(VisitorBasic):
    """ Permission for Member instances. And for group owners in some cases."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if obj.group and user.id == obj.group.owner_id:
            return True
        elif user.id == obj.visitor_id and\
                obj.group.member_set.filter(visitor_id=user.id).exists():
            return True
        return request.user.is_staff


class IsPhotoOwnerOrReadOnly(VisitorBasic):
    """ Only for PhotoViewSet! """

    def has_permission(self, request, view):
        if view.action == 'partial_update':
            return True
        return super(IsPhotoOwnerOrReadOnly, self).has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action == 'partial_update' and 'checksum' in request.data:
            return True
        if view.action == 'clone':
            return True
        user = request.user
        if user.id == obj.visitor_id:
            return True

        return request.user.is_staff
