from __future__ import unicode_literals

from django.contrib.admin.sites import AdminSite
from django.utils.translation import ugettext_lazy as _
from . import forms


class VendorAdminSite(AdminSite):
    site_header = _('Welcome to the business center')
    site_title = _('Business Center')
    index_title = _('Vendor`s Dashboard')

    login_form = forms.VendorAuthForm

    def has_permission(self, request):
        user = request.user
        return True if user.groups.filter(name='vendors').exists() and \
                       user.is_active else False

site = VendorAdminSite('vendor_admin')
