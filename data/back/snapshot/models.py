from __future__ import unicode_literals

from datetime import timedelta
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from visitor.models import Visitor
from utils.utils import UploadPath
from utils.validators import SizeValidator
from vutils.notification import trigger_notification


class MirrorQuerySet(models.query.QuerySet):
    def lock(self):
        return self.update(is_locked=True, lock_date=timezone.now(),
                           last_login=timezone.now())

    def unlock(self):
        return self.update(is_locked=False, last_login=timezone.now())


class MirrorManager(models.Manager):
    def get_queryset(self):
        return MirrorQuerySet(self.model, using=self._db)

    def lock(self):
        return self.get_queryset().lock()

    def unlock(self):
        return self.get_queryset().unlock()

    def get_by_distance(self, lat, lon):
        # IT IS NOT MY QUERY
        sql = "SELECT * FROM (SELECT id,longitude,latitude, " \
              "is_locked, owner_id, " \
              "ROUND(6378.138*2*ASIN(SQRT(POW(SIN((%s*PI()/" \
              "180-latitude*PI()/180)/2),2)+COS(%s*PI()/180)" \
              "*COS(latitude*PI()/180)" \
              "*POW(SIN((%s*PI()/180-longitude*PI()/180)/2),2)))*1000) " \
              "AS distance FROM snapshot_mirror ORDER BY distance LIMIT 10) s " \
              "WHERE  distance < 500"
        return self.raw(sql, [lat, lat, lon])


class PhotoManager(models.Manager):
    def get_queryset(self):
        qs = super(PhotoManager, self).get_queryset()
        qs = qs.annotate(comment_count=models.Count('comment', distinct=True))
        qs = qs.annotate(clone_count=models.Count('clone', distinct=True))
        qs = qs.annotate(like_count=models.Count('like', distinct=True))
        return qs


class ActivePhotoManager(PhotoManager):
    def get_queryset(self):
        qs = super(ActivePhotoManager, self).get_queryset()
        qs = qs.filter(group__isnull=False)
        return qs


class GroupManager(models.Manager):
    def get_queryset(self):
        qs = super(GroupManager, self).get_queryset()
        qs = qs.annotate(photo_count=models.Count('photo', distinct=True))
        return qs


class Mirror(models.Model):
    """ OLD Model is sucks.
    This model is based on the old one.
    So it is not a perfect too. """
    title = models.CharField(_('Title'), max_length=200, blank=True)
    owner = models.ForeignKey(Visitor, null=True,
                              verbose_name=_('Mirror`s owner'),
                              help_text=_('Mirror`s last user'))
    location = models.CharField(_('Location'), max_length=200, blank=True)
    latitude = models.DecimalField(_('Latitude'), max_digits=19,
                                   decimal_places=10)
    longitude = models.DecimalField(_('Longitude'), max_digits=19,
                                    decimal_places=10)
    # Formerly known as device_tokens
    token = models.CharField(_('Device tokens'), max_length=200, unique=True)
    create_date = models.DateTimeField(_('Date created'), auto_now_add=True)
    modify_date = models.DateTimeField(_('Date modified'), auto_now=True)
    lock_date = models.DateTimeField(_('Date locked'), default=timezone.now)
    is_locked = models.BooleanField(_('Locked'), default=False)
    # Formerly online_time
    last_login = models.DateTimeField(_('Last login'), default=timezone.now)

    objects = MirrorManager()

    def update_last_login(self):
        """ Update mirror`s last login.
        Required for mirror status (online) and other things."""
        # Maybe better to replace the code into manager.
        # Update login, when it is necessary
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

    def lock(self):
        """ Sets :is_locked to True and refreshes lock_date (to now)."""
        self.is_locked = True
        self.lock_date = timezone.now()
        self.save(update_fields=['is_locked', 'is_locked'])

    def is_online(self):
        """Checks is mirror online or not (based on last_login date.
        Return True or False."""
        return timezone.now() < (self.last_login + timedelta(seconds=66))

    def is_overtime(self):
        """ Checks mirror is overtime. To return True it must be locked
         and current time must be less then (modify date + 1 minute"""
        # Looks like something stupid
        # It checks only locked mirrors, so maybe in this
        # condition you have to remove "mirror.is_locked"
        if self.is_locked and \
                        timezone.now() < (self.modify_date + timedelta(minutes=1)):
            return True
        return False

    def __unicode__(self):
        return self.token

    class Meta:
        verbose_name = _('Mirror')
        verbose_name_plural = _('Mirrors')
        ordering = ('-modify_date',)


class Stamp(models.Model):
    """ Stamp is actually a tag, but we have already model called tag.
        This table / model stores stamps required
        for Photo tagging and searching.
    """
    title = models.CharField(_('Title'), max_length=255, db_index=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Stamp')
        verbose_name_plural = _('Stamp')
        ordering = ('title',)


class Article(models.Model):
    title = models.CharField(max_length=500, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    author = models.ForeignKey('auth.User', verbose_name=_('Author'))
    create_date = models.DateTimeField(_('Date created'), auto_now_add=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')


class Photo(models.Model):
    """Model representing a photo record with extra data.
        Visitor means not instance of :model:`visitor.Visitor`,
        but instance of :model:`auth.User`.
        Name "Visitor" was left to not change all the code.
        Previously only visitors could access to the photos.
    """
    path_photo = UploadPath('snapshot/photo', None, *('visitor',))
    path_thumb = UploadPath('snapshot/photo/thumbs', None, 'thumb',
                            *('visitor',))
    path_crop = UploadPath('snapshot/photo/crops', None, 'crop',
                           *('visitor',))
    path_cover = UploadPath('snapshot/photo/cover', None, 'cover',
                            *('visitor',))
    visitor = models.ForeignKey('auth.User', verbose_name=_('Photo owner'))
    mirror = models.ForeignKey(Mirror, verbose_name=_('Mirror'), blank=True,
                               null=True, on_delete=models.SET_NULL)
    title = models.CharField(_('Title'), max_length=200, blank=True)
    description = models.TextField(_('Description'), null=True,
                                   blank=True, max_length=5000)
    create_date = models.DateTimeField(_('Date created'), auto_now_add=True)
    modify_date = models.DateTimeField(_('Date modified'), auto_now=True)
    group = models.ForeignKey('snapshot.Group', on_delete=models.SET_NULL,
                              null=True, blank=True)
    # Original photo
    photo = models.ImageField(_('Photo'), upload_to=path_photo,
                              null=True, blank=True,
                              validators=[SizeValidator(8)])
    thumb = models.ImageField(_('Thumbnail'), upload_to=path_thumb,
                              null=True, blank=True)
    crop = models.ImageField(_('Cropped photo'), upload_to=path_crop,
                             null=True, blank=True)
    cover = models.ImageField(_('Cover'), upload_to=path_cover,
                              null=True, blank=True)
    creator = models.ForeignKey('auth.User', verbose_name=_('Photo creator'),
                                null=True, blank=True,
                                related_name='+')
    original = models.ForeignKey('self', null=True, blank=True,
                                 verbose_name=_('Original'),
                                 related_name='clones',
                                 related_query_name='clone',
                                 on_delete=models.SET_NULL)
    stamps = models.ManyToManyField(Stamp, through='PhotoStamp', blank=True)
    article = models.ForeignKey('snapshot.Article', null=True, blank=True,
                                on_delete=models.SET_NULL)
    address = models.CharField(_('Address'), max_length=300,
                               blank=True, null=True)
    objects = models.Manager()
    p_objects = PhotoManager()
    a_objects = ActivePhotoManager()

    def get_comment_count(self):
        """ Returns count of comments."""
        return self.comment_count

    def __unicode__(self):
        return '{}: {}'.format(self.visitor_id, self.pk)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.creator:
            self.creator = self.visitor

        super(Photo, self).save(force_insert, force_update,
                                using, update_fields)

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')
        ordering = ('pk',)


class PhotoStamp(models.Model):
    """ Model representing a tag related with photo, Useful for searching.
    """
    photo = models.ForeignKey(Photo, verbose_name=_('Photo'))
    stamp = models.ForeignKey(Stamp, verbose_name=_('Stamp'))
    confidence = models.DecimalField(_('Confidence'), db_index=True,
                                     max_digits=18, decimal_places=15)

    def __unicode__(self):
        return '{}: {}'.format(self.photo_id, self.stamp)

    class Meta:
        verbose_name = _('Photo stamp')
        verbose_name_plural = _('Photo stamps')
        ordering = ('-confidence', 'pk')
        unique_together = ('photo', 'stamp')


class Comment(models.Model):
    """This model represents comment belonged to the instance of :model:`auth.User`
    (user) and adressed for the instance of  :model:`snapshot.Photo` (photo).
    So it is represents relation between user and photo,
    with some additional fields.
    """
    photo = models.ForeignKey(Photo, verbose_name=_('Photo'),
                              on_delete=models.CASCADE)
    author = models.ForeignKey('auth.User', verbose_name=_('Author'))
    message = models.CharField(_('Message'), max_length=160)
    create_date = models.DateTimeField(_('Date created'), auto_now_add=True)
    modify_date = models.DateTimeField(_('Date modified'), auto_now=True)
    like = models.PositiveIntegerField(_('Like counter'), default=0)

    def __unicode__(self):
        return '{}:{}:{}'.format(self.photo, self.id, self.author)

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ('create_date', 'pk')


class Like(models.Model):
    """ A table that stores relation between :model:`snapshot.Photo` (photo)
     and :model:`auth.User` (visitor).
    If such connection exists then we can say, that user likes the photo.
    It is some kind of Many-to-Many relation.
    But i make an independent model for this case to have more control with
    data and data migration."""
    photo = models.ForeignKey(Photo, verbose_name=_('Photo'))
    visitor = models.ForeignKey('auth.User', verbose_name=_('Visitor'))
    like_date = models.DateTimeField(_('Date Started Like'), auto_now_add=True)

    def __unicode__(self):
        return '{}:{}'.format(self.photo, self.visitor.id)

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')
        ordering = ('pk',)
        unique_together = ('photo', 'visitor')


class Link(models.Model):
    """ A table that stores relation between :model:`snapshot.Photo` (photo)
        and :model:`catalog.Commodity` (commodity).
        Each photo can contain three (3) references to different commodities.
        This constraint will be resolved with help of view or serializer.
        This relation takes sense only
        if owner of the photo (:model:`auth.User`) is vendor (store).
    """
    photo = models.ForeignKey(Photo, verbose_name=_('Photo'))
    commodity = models.ForeignKey('catalog.Commodity',
                                  verbose_name=_('Commodity'))

    class Meta:
        verbose_name = _('Commodity Link')
        verbose_name_plural = _('Commodity Links')
        ordering = ('pk',)
        unique_together = ('photo', 'commodity')


class Group(models.Model):
    """ This model represents :model:`auth.User` (owner)[virtual] wardrobe. """
    # TODO: who can own the group? Only weixin user or any kind too?
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), max_length=5000,
                                   blank=True)
    is_private = models.BooleanField(_('Private'), default=False)
    create_date = models.DateTimeField(_('Date created'), auto_now_add=True)
    modify_date = models.DateTimeField(_('Date modified'), auto_now=True)
    owner = models.ForeignKey('auth.User', verbose_name=_('Group owner'))

    objects = GroupManager()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
        ordering = ('create_date', 'pk',)


class Member(models.Model):
    """ Representation of a group member.
    It not uses directly ManyToMany Relation. It is realized explicitly.
    Relation between :model:`auth.User` (visitor)
    and :model:`snapshot.Group` (group).
    """
    # TODO: implement feature:
    # only store`s can be members of the store`s group
    # only visitors (wechat) can be members of the visitor`s group
    group = models.ForeignKey(Group, verbose_name=_('Group'),
                              on_delete=models.CASCADE)
    visitor = models.ForeignKey('auth.User', verbose_name=_('Visitor'),
                                on_delete=models.CASCADE)

    def __unicode__(self):
        return '{}, {}'.format(self.group, self.visitor)

    class Meta:
        verbose_name = _('Collaborator')
        verbose_name_plural = _('Collaborators')
        ordering = ('pk',)


class Tag(models.Model):
    """ Representation of tag for :model:`snapshot.Group`.
     Can be used for search. """
    title = models.CharField(_('Title'), max_length=200, blank=True)
    group = models.ForeignKey(Group, verbose_name=_('Group'))
    visitor = models.ForeignKey('auth.User', verbose_name=_('Visitor'))

    def __unicode__(self):
        return '{}, {}'.format(self.group_id, self.title)

    class Meta:
        verbose_name = _('Group tag')
        verbose_name_plural = _('Group tags')
        ordering = ('pk',)


class FollowGroup(models.Model):
    """
    Representation of follers for a group.
    Relation between :model:`auth.User` (visitor)
    and :model:`snapshot.Group` (group).
    """

    group = models.ForeignKey(Group, verbose_name=_('Group'),
                              on_delete=models.CASCADE)
    follower = models.ForeignKey('auth.User', verbose_name=_('Follower'),
                                 on_delete=models.CASCADE,
                                 related_name='follow_groups',
                                 related_query_name='follow_group')
    follow_date = models.DateTimeField(_('Date Started Following'), auto_now_add=True)

    def __unicode__(self):
        return '{}, {}'.format(self.group, self.follower)

    class Meta:
        verbose_name = _('Group Follower')
        verbose_name_plural = _('Group Followers')
        unique_together = (('group', 'follower'),)
        ordering = ('pk',)


class FollowUser(models.Model):
    """
    Representation of followers for a user.
    Relation between :model:`auth.User` (visitor)
    and :model:`auth.User` (follower).
    """
    user = models.ForeignKey('auth.User', verbose_name=_('User'),
                             on_delete=models.CASCADE)

    follower = models.ForeignKey('auth.User', verbose_name=_('Follower'),
                                 on_delete=models.CASCADE,
                                 related_name='follow_users',
                                 related_query_name='follow_user')
    follow_date = models.DateTimeField(_('Date Started Following'), auto_now_add=True)

    def __unicode__(self):
        return '{}, {}'.format(self.user, self.follower)

    class Meta:
        verbose_name = _('User Follower')
        verbose_name_plural = _('User Followers')
        unique_together = (('user', 'follower'),)
        ordering = ('pk',)


class Notification(models.Model):
    """
    Representation of notification
    """
    type = models.CharField(max_length=50, default='success')
    message = models.CharField(max_length=500)
    create_date = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', verbose_name=_('User'),
                              on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='new')

    def __unicode__(self):
        return '{}: {}'.format(self.owner, self.message)

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)
        if self.status == 'new':
            trigger_notification('nf_channel_{}'.format(self.owner.id),
                                 'new_notification', self.message, self.type,
                                 self.id, self.create_date)

    class Meta:
        ordering = ('pk',)
