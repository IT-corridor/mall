from __future__ import unicode_literals

from rest_framework import pagination
from rest_framework.response import Response
from collections import OrderedDict


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('current', self.page.number),
            ('total', self.page.paginator.num_pages),
            ('next_page', self.get_next_page()),
            ('previous_page', self.get_previous_page()),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_next_page(self):
        if not self.page.has_next():
            return None
        return self.page.next_page_number()

    def get_previous_page(self):
        if not self.page.has_previous():
            return None
        return self.page.previous_page_number()
