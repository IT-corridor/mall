from __future__ import unicode_literals

import os
import time
from django.conf import settings
from django.db.models import Count
from django.core.management.base import BaseCommand, CommandError
from snapshot.models import Photo, Stamp, PhotoStamp
from utils.api import ImaggaAPI


class Command(BaseCommand):
    help = 'Fetches tags for photos from imagga.com service'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            '--lang',
            dest='lang',
            help='Specify language',
            type=str,
        )

    def handle(self, *args, **options):

        lang = options['lang'] if options.get('lang') else settings.IMAGGA_LANG

        # here we choose only that photos that have no tags,
        # to reduce amount of request
        photos = Photo.objects.annotate(Count('stamps'))\
            .filter(stamps__count=0)
        total = len(photos)
        success = 0
        skipped = 0
        self.stdout.write(
            self.style.WARNING('{} photos need to be processed'
                               .format(total)
                               )
        )

        for n, instance in enumerate(photos):
            self.stdout.write(
                self.style.WARNING('Processing {} item of {}'
                                   .format(n, total)
                                   )
            )
            try:
                if not instance.thumb or not instance.thumb.name:
                    self.stdout.write(str('No thumb found'))
                    continue

                path = instance.thumb.path
                if path and os.path.isfile(path):
                    api = ImaggaAPI()
                    response = api.get_tags_by_filepath(path, language=lang)
                    # No need exception handling on this stage
                    tags = response['results'][0]['tags']

                    for i in tags:
                        stamp, _ = Stamp.objects.get_or_create(title=i['tag'])
                        PhotoStamp.objects.create(photo=instance, stamp=stamp,
                                                  confidence=i['confidence'])
                time.sleep(1)
            except Exception as e:
                self.stdout.write(self.style.ERROR(e.message))
                skipped += 1
            else:
                success += 1

        self.stdout.write(self.style.SUCCESS('Task has been finished!'))
        self.stdout.write(self.style.SUCCESS('Total:{}, success: {}, skipp: {}'
                                             .format(total, success, skipped)))
