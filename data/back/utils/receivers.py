from __future__ import unicode_literals

from .utils import create_thumb, create_crop, cleanup_files, cleanup_if_none, \
    max_ratio, create_cover
from vutils.register_quickblox_user import user_signup_qb


def create_thumb_avatar(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_thumb(instance, 'avatar')


def create_thumb_photo(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_thumb(instance, 'photo')


def create_thumb_photo_320(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_thumb(instance, 'photo', 320)


def create_thumb_photo_500(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_thumb(instance, 'photo', 500)


def create_max_thumb_photo_500(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_thumb(instance, 'photo', 500, ratio_f=max_ratio)


def create_cover_photo_320(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_crop(instance, 'photo', 320, 'cover')


def create_thumb_avatar_320(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_thumb(instance, 'avatar', 320)


def create_crop_photo_100(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_crop(instance, 'photo', 100)


def create_crop_photo_120(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_crop(instance, 'photo', 120)


def create_cover_photo_900(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        create_cover(instance, 'photo', 900)


def cleanup_files_avatar(sender, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance = kwargs.get('instance', None)
    if instance:
        cleanup_files(instance, 'avatar')


def cleanup_files_photo(sender, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance = kwargs.get('instance', None)
    if instance:
        cleanup_files(instance, 'photo')


def cleanup_if_avatar_is_none(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        cleanup_if_none(instance, 'avatar')


def register_quickblox(sender, instance, created, **kwargs):
    # TODO: maybe it make sence to handle it with django_rq
    if instance and created:
        user_signup_qb(instance)
