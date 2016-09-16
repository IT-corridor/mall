from __future__ import unicode_literals

import os
from django.core.management.base import BaseCommand, CommandError
from catalog.models import Gallery


class Command(BaseCommand):
    help = 'Refresh secondary remakes secondary photos (thumbs, crops)' \
           ' for commodity galleries'

    def handle(self, *args, **options):

        photos = Gallery.objects.all()
        for photo in photos:
            print photo
            if photo.photo and os.path.isfile(photo.photo.path):
                photo.crop.delete(True)
                photo.thumb.delete(True)
                photo.cover.delete(True)
                photo.save()

        self.stdout.write(
            self.style.SUCCESS('Gallery photos have been refreshed!'))
