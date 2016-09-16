from __future__ import unicode_literals

from rest_framework.response import Response


class OwnerCreateMixin(object):
    """ Needed for views / viewsets,
     where user data taken from session or not directly.
      Works only if owner is instance of user
      (or its related model without own pk"""

    user_kwd = 'owner'

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data[self.user_kwd] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class OwnerUpdateMixin(object):

    user_kwd = 'owner'

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data[self.user_kwd] = request.user.id
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class VisitorCreateMixin(OwnerCreateMixin):
    user_kwd = 'visitor'


class PaginationMixin(object):
    def get_list_response(self, queryset, serializer_class):
        """ Shortcut for the paginated views / handlers """
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        context = {'request': self.request}
        if page is not None:
            serializer = serializer_class(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)


class AjaxMixin(object):

    def get(self, request, *args, **kwargs):
        if request.is_ajax() or request.user.is_staff:
            return super(AjaxMixin, self).get(request, *args, **kwargs)
        else:
            return Response(status=403)
