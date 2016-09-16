from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from utils.validators import validate_weixin
from . import models


class ChineseUserCreationForm(UserCreationForm):
    username_c = forms.CharField(label=_('Username'), max_length=30,
                              validators=[validate_weixin],
                              help_text=_('4-30 characters, '
                                          'Chinese and English letters,'
                                          ' numbers, -, _'))

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_username_c(self):
        username = self.cleaned_data.get('username_c')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('A user with that username already exists.'))
        self.instance.username = username
        print (self.instance)
        return username

    class Meta:
        model = User
        exclude = '__all__'


class VendorInline(admin.StackedInline):
    model = models.Vendor
    extra = 0


class AdminVendor(UserAdmin):
    """ Creation form has been changed. Because it is an easiest path
    to implement 'chinese usernames'. For edit form,
    I was set username read_only = True, because it will also not validate
    chinese characters --- because we use basic django model"""
    add_form = ChineseUserCreationForm
    list_display = ('username', 'email', 'first_name')
    inlines = VendorInline,

    readonly_fields = ('username',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username_c', 'password1', 'password2'),
        }),
    )


class AdminStore(admin.ModelAdmin):

    list_display = ('brand_name', 'district', 'get_location')
    list_filter = ('district',)
    list_select_related = ('district__city__state',)

admin.site.unregister(User)
admin.site.register(models.State)
admin.site.register(models.City)
admin.site.register(models.District)
admin.site.register(models.Store, AdminStore)
admin.site.register(models.Vendor)
admin.site.register(User, AdminVendor)
