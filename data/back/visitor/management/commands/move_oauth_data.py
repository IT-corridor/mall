from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from visitor.models import Visitor, VisitorExtra
from django.db.models import Q

class Command(BaseCommand):
    help = 'Moves oauth2 data to another (related) table'

    def handle(self, *args, **options):
        VisitorExtra.objects.all().delete()
        visitors = Visitor.objects.all()
        errors = []
        for data in visitors:
            try:
                VisitorExtra.objects.create(
                    openid=data.weixin,
                    access_token=data.access_token,
                    refresh_token=data.refresh_token,
                    expires_in=data.expires_in,
                    token_date=data.token_date,
                    visitor_id=data.pk
                )
            except Exception as e:
                errors.append((e.message, data))
                self.stdout.write(
                    self.style.WARNING(e.message))
        if errors:
            for error, obj in errors:
                self.stdout.write(
                    self.style.DANGER('Error {}, Objgect.id {}'
                                      .format(error, obj.id)))
        self.stdout.write(
            self.style.SUCCESS('OAuth2 data has been moved!'))
