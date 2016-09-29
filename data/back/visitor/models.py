from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from utils.validators import validate_weixin, china_phone
from utils.validators import SizeValidator
from utils.fields import EmailNullField, CharNullField


class Visitor(models.Model):
    """ This model extends basic authentication model (of Django).
    It used to authenticate user ONLY via WECHAT (WEXIN) API. """
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE,
                                primary_key=True)
    avatar = models.ImageField(_('Avatar'), upload_to='visitors',
                               null=True, blank=True,
                               validators=[SizeValidator(0.5)])
    thumb = models.ImageField(_('Thumbnail'),
                              upload_to='visitors/thumbs',
                              null=True, blank=True)
    # blanked for the compatibility existing data
    # this username is NOT unique
    username = models.CharField(_('Username'), max_length=30, blank=True)
    phone = CharNullField(_('Phone'), max_length=16, blank=True, null=True,
                          validators=[china_phone], unique=True, default=None)
    email = EmailNullField(_('Email'), unique=True, blank=True, null=True,
                           default=None)

    def __unicode__(self):
        return self.username if self.username else self.user.username

    class Meta:
        verbose_name = _('Visitor')
        verbose_name_plural = _('Visitors')


class Weixin(models.Model):
    """ Only for weixjn data """
    visitor = models.OneToOneField(Visitor, on_delete=models.CASCADE,
                                   primary_key=True, verbose_name=_('visitor'))
    # blanked for the compatibility existing data
    unionid = models.CharField(_('Union ID'), max_length=40,
                               blank=True, db_index=True)

    def __unicode__(self):
        return '{}: {}'.format(self.visitor, self.unionid)

    class Meta:
        verbose_name = _('Weixin')


class VisitorExtra(models.Model):
    """ This model contains extra data from oauth2 wechat """
    openid = models.CharField(_('Weixin open id'), max_length=30,
                              validators=[validate_weixin], unique=True,
                              help_text=_('4-30 characters, '
                                          'Chinese and English letters,'
                                          ' numbers, -, _'))
    access_token = models.CharField(_('Weixin Access Token'), max_length=255)
    refresh_token = models.CharField(_('Weixin Refresh Token'), max_length=255)
    expires_in = models.PositiveIntegerField(_('Token expires in'))
    token_date = models.DateTimeField(_('Token date'), default=timezone.now)
    backend = models.CharField(_('Auth backend'), max_length=50,
                               default='weixin')
    weixin = models.ForeignKey(Weixin, verbose_name=_('Weixin'),
                               null=True, blank=True)

    def is_expired(self):
        """Not a field --- it is a method. Checks if token is expired.
        Returns True or False."""
        return timezone.now() > \
               self.token_date + timezone.timedelta(seconds=self.expires_in)

    class Meta:
        verbose_name = _('Extra Data')
        unique_together = (('weixin', 'backend'),)


class Quickblox(models.Model):
    """ Qucikblox credentials vault """
    qid = models.PositiveIntegerField(_('Quickblox external ID'))
    login = models.CharField(_('Login'), max_length=50)
    full_name = models.CharField(_('Full name'), max_length=50)
    password = models.CharField(_('Password'), max_length=50)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE,
                                primary_key=True)

    class Meta:
        verbose_name = _('Quickblox')
        ordering = ('pk',)
