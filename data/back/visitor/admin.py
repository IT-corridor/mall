from __future__ import unicode_literals
from django.contrib import admin
from . import models
# Register your models here.


class VisitorAdmin(admin.ModelAdmin):

    list_display = ('user',)


class VisitorExtraAdmin(admin.ModelAdmin):
    list_display = ('weixin', 'is_expired')
    readonly_fields = ('openid', 'access_token', 'refresh_token',
                       'expires_in', 'token_date',)


class WeixinAdmin(admin.ModelAdmin):
    readonly_fields = ('unionid', )


class QuickbloxAdmin(admin.ModelAdmin):
    list_display = ('qid', 'login', 'full_name',)

admin.site.register(models.Visitor, VisitorAdmin)
admin.site.register(models.Weixin, WeixinAdmin)
admin.site.register(models.VisitorExtra, VisitorExtraAdmin)
admin.site.register(models.Quickblox, QuickbloxAdmin)
