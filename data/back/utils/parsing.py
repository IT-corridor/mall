from __future__ import unicode_literals

from django.utils.six.moves import StringIO
from rest_framework import parsers


def parse_json_data(data):
    """Useful when json send via FormData (because of attaced files)."""
    stream = StringIO(data)
    data = parsers.JSONParser().parse(stream)
    return data