from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from utils.validators import SizeValidator
from utils import utils, receivers


class AbsCategory(models.Model):
    """ Each record of ref. model has its own title and priority for sorting"""
    title = models.CharField(_('Title'), max_length=50)
    priority = models.PositiveSmallIntegerField(_('Priority'), default=0)


    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class AbsStoreCategory(AbsCategory):
    """Extends :model:`AbsCategory with :model:`snapshot.Store` reference."""
    store = models.ForeignKey('account.Store', verbose_name=_('Store'))

    class Meta:
        abstract = True


class Category(AbsCategory):
    """ AKA CATALOG 1. Can be set only by the administrator of the platform."""

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ('priority', 'pk')


class Kind(AbsCategory):
    """ AKA CATALOG 2.
    Can be set only by the administrator of the platform. """
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    class Meta:
        verbose_name = _('Kind')
        verbose_name_plural = _('Kinds')
        ordering = ('priority', 'pk')


class Brand(AbsStoreCategory):
    """ Brand of the :model:`catalog.Commodity`"""
    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        ordering = ('priority', 'pk')


class Color(AbsCategory):
    """ Color of the :model:`catalog.Commodity`"""
    html = models.CharField(_('Html code'), max_length=7, blank=True)

    class Meta:
        verbose_name = _('Color')
        verbose_name_plural = _('Colors')
        ordering = ('priority', 'pk')


class Size(AbsCategory):
    """ Size for the :model:`catalog.Commodity`.
    Optionally can contain :model:`catalog.Commodity` foreign key.
    Because some categories, like shoes, can have different size system """
    category = models.ForeignKey(Category, verbose_name=_('Category'),
                                 blank=True, null=True)

    class Meta:
        verbose_name = _('Size')
        verbose_name_plural = _('Sizes')
        ordering = ('priority', 'pk')


class Commodity(models.Model):
    """ Basic Commodity. Because of RFID,
    we need to create each time a new instance of commodity,
    even if they differ only by color or size."""
    SEASONS = (
        ('0', _('Winter')),
        ('1', _('Spring')),
        ('2', _('Summer')),
        ('3', _('Autumn')),
    )
    title = models.CharField(_('Title'), max_length=100, blank=True)
    description = models.TextField(_('Description'), null=True,
                                   blank=True, max_length=5000)
    # Better use regex field for year.
    year = models.CharField(_('Year'), max_length=4)
    season = models.CharField(_('Season'), choices=SEASONS, max_length=1)
    add_date = models.DateTimeField(_('Date added'), auto_now_add=True)
    modify_date = models.DateTimeField(_('Date modified'), auto_now=True)
    kind = models.ForeignKey(Kind, verbose_name=_('Kind'))
    brand = models.ForeignKey(Brand, verbose_name=_('Brand'))
    store = models.ForeignKey('account.Store', verbose_name=_('Store'))
    colors = models.ManyToManyField(Color, through='Stock',
                                    verbose_name=_('Colors'))
    sizes = models.ManyToManyField(Size, through='Stock',
                                   verbose_name=_('Sizes'))

    def __unicode__(self):
        # BRAND+KIND+YEAR
        """String representation of the commodity instance."""
        return self.title if self.title else \
            '{}+{}+{}'.format(self.brand, self.kind, self.year)

    class Meta:
        verbose_name = _('Commodity')
        verbose_name_plural = _('Commodities')
        ordering = ('id',)


class Stock(models.Model):
    """ Represents a sub-item of the :model:`catalog.Commodity`
    with different color, size and amount. """
    commodity = models.ForeignKey(Commodity, verbose_name=_('Commodity'))
    color = models.ForeignKey(Color, verbose_name=_('Color'),
                              blank=True, null=True)
    size = models.ForeignKey(Size, verbose_name=_('Size'))

    color_extra = models.CharField(_('Extra color'), max_length=50, blank=True,
                                   help_text=_('Useful if vendor did not '
                                               'find required color'))
    color_pic = models.ImageField(_('Sample of color'), blank=True, null=True,
                                  upload_to='colors')
    amount = models.PositiveIntegerField(_('Amount'), default=0)

    def get_title(self):
        c = self.commodity
        return '{}+{}+{}+{}+{}'.format(c.brand, self.color, c.kind,
                                       self.size, self.year)

    class Meta:
        verbose_name = _('Stock')
        verbose_name_plural = _('Stocks')
        ordering = ('id',)
        unique_together = (('commodity', 'color', 'size'),)


class Gallery(models.Model):
    """Represent one additional photo for the :model:`catalog.Commodity`.
    So it is some kind of gallery.
    Each commodity can have many additional photo (gallery)."""
    # TODO: add a count constraint for the commodity equal 5
    # TODO: make it with viewset in the perform_create

    path_photo = utils.UploadPath('gallery', 'commodity')
    path_thumb = utils.UploadPath('gallery/thumbs', 'commodity', suff='thumb')
    path_crop = utils.UploadPath('gallery/crops', 'commodity', suff='crop')
    path_cover = utils.UploadPath('gallery/covers', 'commodity', suff='cover')

    commodity = models.ForeignKey(Commodity, verbose_name=_('Commodity'))
    photo = models.ImageField(_('Photo'), upload_to=path_photo,
                              validators=[SizeValidator(15)])
    thumb = models.ImageField(_('Thumbnail'), upload_to=path_thumb,
                              null=True, blank=True)
    crop = models.ImageField(_('Cropped photo'), upload_to=path_crop,
                             null=True, blank=True)
    cover = models.ImageField(_('Cover photo'), upload_to=path_cover,
                              null=True, blank=True)

    class Meta:
        verbose_name = _('Gallery')
        verbose_name_plural = _('Gallery')
        ordering = ('id',)


class Tag(models.Model):
    """ Represent one tag for the :model:`catalog.Commodity`.
    Each commodity can have many tags."""
    title = models.CharField(_('Title'), max_length=50)
    commodity = models.ForeignKey(Commodity, verbose_name=_('Commodity'))

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ('id',)


class Event(models.Model):
    store = models.ForeignKey('account.Store', verbose_name=_('Store'))
    create_date = models.DateTimeField(auto_now=True)
    type = models.CharField(_('Event Type'), max_length=50)
    description = models.TextField(_('Description'))

    def __unicode__(self):
        return self.store.name

    class Meta:
        ordering = ('-id',)


class Promotion(models.Model):
    store = models.ForeignKey('account.Store', verbose_name=_('Store'))
    create_date = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(null=True)
    post = models.ImageField(_('Post'), upload_to='promotions',
                             blank=True, null=True)
    description = models.TextField(_('Description'))

    def __unicode__(self):
        return self.store.name

    class Meta:
        ordering = ('-id',)
