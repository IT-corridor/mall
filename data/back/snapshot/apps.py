from __future__ import unicode_literals

from django.apps import AppConfig


class SnapshotConfig(AppConfig):
    name = 'snapshot'

    def ready(self):
        from django.db.models.signals import pre_delete, post_save
        from .receivers import fetch_tags
        from .receivers import send_notification
        from utils import receivers

        Photo = self.get_model('Photo')
        Notification = self.get_model('Notification')

        pre_delete.connect(receivers.cleanup_files_photo, sender=Photo)
        post_save.connect(receivers.create_max_thumb_photo_500, sender=Photo)
        post_save.connect(receivers.create_crop_photo_100, sender=Photo)
        post_save.connect(receivers.create_cover_photo_320, sender=Photo)
        post_save.connect(fetch_tags, sender=Photo)
        post_save.connect(send_notification, sender=Notification)
