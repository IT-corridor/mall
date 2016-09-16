from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


def validate_weixin(value):
    error = _('Enter a valid weixin id. This value may contain only '
              'English and Chinese letters, numbers and -, _ characters.')
    validator = RegexValidator(u'^[\w\d\-\u2E80-\u9FFF]+$', error)
    return validator(value)
