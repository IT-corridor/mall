from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from .models import Quickblox
from utils.quickblox import QuickbloxAPI


def quickblox_sign_up(sender, instance=None, created=False, **kwargs):
    if instance and created:
        api = QuickbloxAPI(settings.QUICKBLOX_APP_ID,
                           settings.QUICKBLOX_AUTH_KEY,
                           settings.QUICKBLOX_AUTH_SECRET)
        user = instance.user
        password = User.objects.make_random_password()
        token = api.get_token()
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
