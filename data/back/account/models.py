from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from utils.validators import SizeValidator, phone_regex
from utils.fields import EmailNullField, CharNullField


# Create your models here.


class Vendor(models.Model):
    """This model represents a vendor instance.
    This model do not has own primary key,
    it uses foreign key of :model:`auth.User` as primary key.
    Maybe it is really redundant. But it is currently useful to create a vendor
    offline and after that vendor can login and create one store.
    We can`t use django user`s email. Because it is too late. It is not unique.
    And if i will change user model for new custom model,
    it will break migrations.
    """
    # TODO: Fix auto creation with empty params
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                primary_key=True)

    avatar = models.ImageField(_('Avatar'), upload_to='vendors',
                               null=True, blank=True,
                               validators=[SizeValidator(0.5)])
    thumb = models.ImageField(_('Thumbnail'),
                              upload_to='vendors/thumbs',
                              null=True, blank=True)
    phone = CharNullField(_('Phone'), max_length=16, blank=True, null=True,
                          validators=[phone_regex], unique=True, default=None)
    email = EmailNullField(_('Email'), unique=True, blank=True, null=True,
                           default=None)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')


class AbsLocation(models.Model):
    title = models.CharField(_('Title'), db_index=True, max_length=100)

    class Meta:
        abstract = True


class State(AbsLocation):
    """Representation of state. It has own model to avoid data duplication.
    Also it can be useful for the search."""

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')
        ordering = ('id',)

    def __unicode__(self):
        return self.title


class City(AbsLocation):
    """Representation of City. Reason the same as :model:`account.State` has.
    """
    state = models.ForeignKey(State, verbose_name=_('State'))

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __unicode__(self):
        return '{},{}'.format(self.state, self.title)


class District(AbsLocation):
    """Representation of district. Reason the same as
    :model:`account.State` has."""
    city = models.ForeignKey(City, verbose_name=_('City'))

    class Meta:
        verbose_name = _('Districts')
        verbose_name_plural = _('Districts')

    def __unicode__(self):
        return '{},{}'.format(self.city, self.title)


class Store(models.Model):
    """ Representation of the store."""
    district = models.ForeignKey(District, verbose_name=_('District'))

    address = models.CharField(_('Address'), max_length=300,
                               blank=True, null=True)
    lat = models.CharField(_('Latitude'), max_length=50,
                           blank=True, null=True)
    lng = models.CharField(_('Longitude'), max_length=50,
                           blank=True, null=True)
    introduction = models.TextField(_('Introduction of the store'), blank=True,
                                    null=True)
    street = models.CharField(_('Street'), max_length=100,
                           blank=True, null=True)
    street_no = models.CharField(_('Street number'), max_length=100,
                           blank=True, null=True)
    build_name = models.CharField(_('Building name'), max_length=50,
                                  blank=True)
    build_no = models.CharField(_('Building number'), max_length=5,
                           blank=True, null=True)
    apt = models.CharField(_('Apartments'), max_length=5,
                           blank=True, null=True)
    brand_name = models.CharField(_('Brand name'), max_length=50, unique=True)
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE,
                                  verbose_name=_('Owner'), primary_key=True)
    crop = models.ImageField(_('Crop'), upload_to='stores/crops',
                             null=True, blank=True)
    photo = models.ImageField(_('Logo'), upload_to='stores',
                              blank=True, null=True)
    post = models.ImageField(_('Post'), upload_to='stores/post',
                             blank=True, null=True)
    name = models.CharField(_('Store name'), max_length=150)

    def get_location(self):
        """ It is not a field --- it is a method. It returns an address string,
         based on state, city, district and other own properties."""
        return '{},{}{}{}{}{}'.format(self.district, self.street,
                                      self.street_no, self.build_name,
                                      self.build_no, self.apt)

    def __unicode__(self):
        return self.brand_name
