from __future__ import unicode_literals

from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


@deconstructible
class SizeValidator(BaseValidator):
    compare = lambda self, a, b: a > b * 1024 * 1024
    clean = lambda self, x: x.size
    message = _('Max file size is %(limit_value)s MB.')
    code = 'file_size_value'
