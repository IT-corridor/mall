from __future__ import unicode_literals
from django.contrib.auth.forms import AuthenticationForm


class VendorAuthForm(AuthenticationForm):

    def confirm_login_allowed(self, user):
        return True if user.groups.filter(name='vendors').exists() and \
                       user.is_active else False
