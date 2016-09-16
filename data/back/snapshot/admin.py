from __future__ import unicode_literals

from django.contrib import admin
from . import models


class PhotoInline(admin.TabularInline):
    model = models.Photo
    extra = 0


class CommentInline(admin.TabularInline):
    model = models.Comment
    extra = 0


class LinkInline(admin.TabularInline):
    model = models.Link
    extra = 0


class MirrorAdmin(admin.ModelAdmin):

    list_display = ('title', 'is_locked', 'last_login')
    inlines = (PhotoInline,)


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'visitor', 'mirror', 'group')
    search_fields = ('title', 'stamps__title')
    inlines = (CommentInline, LinkInline)
    readonly_fields = ('thumb', 'cover', 'crop', 'creator', 'original')


# GROUP
class MemberInline(admin.TabularInline):
    model = models.Member
    extra = 0


class TagInline(admin.TabularInline):
    model = models.Tag
    extra = 0


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_private')
    inlines = (MemberInline, TagInline)


class PhotoStampAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'photo', 'confidence')
    search_fields = ('stamp__title',)

# REGISTER models to admin
admin.site.register(models.Mirror, MirrorAdmin)
admin.site.register(models.Photo, PhotoAdmin)
admin.site.register(models.Comment)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Stamp)
admin.site.register(models.PhotoStamp, PhotoStampAdmin)
admin.site.register(models.FollowGroup)
admin.site.register(models.FollowUser)
admin.site.register(models.Article)
admin.site.register(models.Notification)
