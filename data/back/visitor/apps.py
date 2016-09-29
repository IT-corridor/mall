from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# THIS IT PT APPLICATION FORMERLY CALLED A'CCOUNTS'


class VisitorConfig(AppConfig):
    name = 'visitor'
    verbose_name = _('Visitor')

    def ready(self):
        from django.db.models.signals import pre_delete, post_save
        from .receivers import quickblox_sign_up
        from utils import receivers

        Visitor = self.get_model('Visitor')
        pre_delete.connect(receivers.cleanup_files_avatar, sender=Visitor)
        post_save.connect(receivers.create_thumb_avatar_320, sender=Visitor)
        post_save.connect(quickblox_sign_up, sender=Visitor)
