from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from visitor.models import VisitorExtra, Weixin
from django.db.models import Q

class Command(BaseCommand):
    help = 'Moves weixin unionid and move visitor_id to weixin_id'

    def handle(self, *args, **options):
        extra = VisitorExtra.objects.filter(weixin__isnull=True)
        for ve in extra:
            weixin, _ = Weixin.objects.get_or_create(visitor=ve.visitor,
                                                     unionid=ve.visitor.unionid)
            ve.weixin = weixin
            ve.save()

        self.stdout.write(
            self.style.SUCCESS('OAuth2 data has been success!'))
