from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from visitor.models import Visitor, Quickblox
from utils.quickblox import QuickbloxAPI


class Command(BaseCommand):
    help = 'Update users full_name at quickblox'

    def handle(self, *args, **options):
        visitors = Visitor.objects.all()
        api = QuickbloxAPI(settings.QUICKBLOX_APP_ID,
                           settings.QUICKBLOX_AUTH_KEY,
                           settings.QUICKBLOX_AUTH_SECRET)
        for n, visitor in enumerate(visitors):
            user = visitor.user
            if hasattr(user, 'quickblox'):
                quickblox = user.quickblox
                try:
                    self.stdout.write(
                        'processing user {}, {}, {}'.format(quickblox.full_name, quickblox.qid, n))

                    token = api.get_token()
                    api.sign_in(quickblox.login, quickblox.password, token)

                    user_data = {'full_name': visitor.username}
                    data = api.update_user_data(quickblox.qid, user_data,
                                                token)

                    quickblox.full_name = data['user']['full_name']
                    quickblox.save()
                    api.destroy_session(token)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(e))
                    self.stdout.write(
                        self.style.WARNING('Error: {}-{},{}'.format(user, user.id, n)))

        self.stdout.write(
            self.style.SUCCESS('All users registered!'))
