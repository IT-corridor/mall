from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from vutils.register_quickblox_user import user_signup_qb


class Command(BaseCommand):
    help = 'Register all users to quickblox'

    def handle(self, *args, **options):
        for user in User.objects.all():
            user_signup_qb(user)
        self.stdout.write(self.style.SUCCESS('done'))
