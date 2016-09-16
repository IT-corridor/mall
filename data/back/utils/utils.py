from __future__ import unicode_literals, division

import os
import imghdr
import requests
from io import BytesIO
from PIL import Image, ImageOps, ExifTags, ImageColor
from django.core.files import File
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile


@deconstructible
class UploadPath(object):
    """ Handling upload path """
    def __init__(self, path, fieldname=None, suff='', *args):
        self.path = path
        self.suff = suff
        self.fieldname = fieldname
        self.subs = args

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        if self.fieldname:
            field = getattr(instance, self.fieldname, None)
            if field:
                filename = '{}-{}.{}'.format(field, self.suff, ext)
        if self.subs:
            subs = tuple(getattr(instance, i).pk for i in self.subs)
            sub = '/'.join(str(i) for i in subs)
        else:
            sub = ''
        return os.path.join(self.path, sub, filename)


def rotate_image(image):
    """ Rotate an image if it is required."""
    if hasattr(image, '_getexif'):
        exif = image._getexif()
        if exif is not None:
            # PYTHON 2!
            # tag = filter(lambda x: x[1] == 'Orientation', ExifTags.TAGS.items())[0]
            # key, value = tag
            # Exif orientation tag
            key = 0x0112
            exif_data = dict(image._getexif().items())
            orientation_tag = exif_data.get(key)
            if orientation_tag:
                if orientation_tag == 3:
                    image = image.rotate(180, expand=True)
                elif orientation_tag == 6:
                    image = image.rotate(270, expand=True)
                elif orientation_tag == 8:
                    image = image.rotate(90, expand=True)
    return image


def max_ratio(w, h, m):
    """
    Order to retrieve a new size of photo
    :param w: Width
    :param h: Height
    :param m: Minimum size of both width and height
    :return: new width, new height
    """
    if w > m and h > m:
        rw = m / w
        rh = m / h
        r = rw if rw > rh else rh
        return int(r*w), int(r*h)
    return w, h


def default_ratio(w, h, m):
    """ This is a opposite of max ratio, this returns new size,
    where m is maximum size for both width and height."""
    if w > m:
        ratio = m / w
        w = m
        h = int(h * ratio)

    if h > m:
        ratio = m / h
        h = m
        w = int(w * ratio)

    return w, h


def get_content_file(url):
    """Creating a django file from content fetched by url"""
    r = requests.get(url)
    ext = r.headers['Content-Type'].split('/')[-1]
    return ext, ContentFile(r.content)


def cleanup_files(instance, fieldname):
    # Pass false so FileField doesn't save the model.
    field = getattr(instance, fieldname)

    if field and hasattr(field, 'name'):
        field.delete(save=False)
    thumb = getattr(instance, 'thumb', None)
    if thumb and hasattr(thumb, 'name'):
        thumb.delete(save=False)

    crop = getattr(instance, 'crop', None)
    if crop and hasattr(crop, 'name'):
        crop.delete(save=False)

    cover = getattr(instance, 'cover', None)
    if cover and hasattr(cover, 'name'):
        cover.delete(save=False)


def cleanup_if_none(instance, fieldname):
    """If main picture is None, remove others (crop, and thumb)"""
    field = getattr(instance, fieldname)

    if not field.name:
        thumb = getattr(instance, 'thumb', None)
        if thumb:
            thumb.delete()

        crop = getattr(instance, 'crop', None)
        if crop:
            crop.delete()


def create_thumb(instance, fieldname, m=100, ratio_f=default_ratio):
    """ Creating a thumb """
    field = getattr(instance, fieldname)
    if field and not instance.thumb.name:
        filename = field.path
        img = Image.open(filename)
        img = rotate_image(img)
        w, h = img.size
        w, h = ratio_f(w, h, m)

        filepath, _ = os.path.splitext(field.name)
        name = filepath.split('/')[-1]
        ext = imghdr.what(filename)
        n_fn = name + '_thumb.' + ext
        img = img.resize((w, h), Image.ANTIALIAS)
        output = BytesIO()
        img.save(output, ext)
        instance.thumb.save(n_fn, File(output), save=True)
        output.close()


def create_crop(instance, input_field, m=100, output_field='crop'):
    crop_field = getattr(instance, output_field)
    field = getattr(instance, input_field)
    if field and not crop_field.name:
        filename = field.path
        img = Image.open(filename)
        img = rotate_image(img)
        w, h = img.size
        if w > h:
            # Ratio does not really matter because it pretty small
            # Crop width
            # Also it can be used ratio_w instead 0.5
            centering = (0.0, 0.5)
        else:
            # Crop height
            centering = (0.5, 0.5)
        cropped = ImageOps.fit(img, (m, m), Image.ANTIALIAS,
                               centering=centering)
        filepath, _ = os.path.splitext(field.name)
        name = filepath.split('/')[-1]
        ext = imghdr.what(filename)
        n_fn = name + '_' + output_field + '.' + ext

        output = BytesIO()
        cropped.save(output, ext)
        crop_field.save(n_fn, File(output), save=True)
        output.close()


def create_cover(instance, input_field, m, output_field='cover', fill=None):
    dest_field = getattr(instance, output_field)
    input_field = getattr(instance, input_field)

    if input_field and not dest_field.name:

        filename = input_field.path

        img = Image.open(filename)
        img = rotate_image(img)
        w, h = img.size
        w, h = default_ratio(w, h, m)

        img = img.resize((w, h), Image.ANTIALIAS)

        # New box

        if w < m:
            x1 = int((m - w) / 2)
            x2 = int(((m - w) / 2) + w)
        else:
            x1 = 0
            x2 = w

        if h < m:
            y1 = int((m - h) / 2)
            y2 = int(((m - h) / 2) + h)
        else:
            y1 = 0
            y2 = h

        box = (x1, y1, x2, y2)

        if fill is None:
            fill = ImageColor.getcolor('white', img.mode)
        base_img = Image.new(img.mode, (m, m), fill)
        base_img.paste(img, box)

        filepath, _ = os.path.splitext(input_field.name)
        name = filepath.split('/')[-1]
        ext = imghdr.what(filename)
        n_fn = name + '_' + output_field + '.' + ext
        output = BytesIO()
        base_img.save(output, ext)
        dest_field.save(n_fn, File(output), save=True)
        output.close()
