from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from visitor.models import Visitor, Quickblox
from utils.quickblox import QuickbloxAPI


class Command(BaseCommand):
    help = 'Register users at quickblox'

    def handle(self, *args, **options):
        visitors = Visitor.objects.all()
        api = QuickbloxAPI(settings.QUICKBLOX_APP_ID,
                           settings.QUICKBLOX_AUTH_KEY,
                           settings.QUICKBLOX_AUTH_SECRET)
        for n, visitor in enumerate(visitors):
            user = visitor.user
            if not hasattr(user, 'quickblox'):
                self.stdout.write('processing user {}, {}, {}'.format(user,
                                                                      user.id, n))
                token = api.get_token()
                password = User.objects.make_random_password()
                r = api.sign_up(user.id, user.username, password, token)

                user_data = {
                    'qid': r['user']['id'],
                    'login': r['user']['login'],
                    'full_name': r['user']['full_name'],
                    'password': password,
                    'user': user,
                }

                Quickblox.objects.create(**user_data)
                api.destroy_session(token)

        self.stdout.write(
            self.style.SUCCESS('All users registered!'))
