from __future__ import unicode_literals

import os
from django.core.management.base import BaseCommand, CommandError
from snapshot.models import Photo


class Command(BaseCommand):
    help = 'Refresh secondary remakes secondary photos (thumbs, crops)'

    def handle(self, *args, **options):

        photos = Photo.objects.all()
        for photo in photos:
            print photo
            if photo.photo and os.path.isfile(photo.photo.path):
                photo.crop.delete(True)
                photo.thumb.delete(True)
                photo.cover.delete(True)
                photo.save()

        self.stdout.write(
            self.style.SUCCESS('Photos have been refreshed!'))
