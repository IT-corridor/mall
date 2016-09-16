# -*- coding: utf-8 -*-
""" Here stored 3d party API`s"""
from __future__ import unicode_literals
import os
import random
from string import ascii_letters, digits
import requests
from django.conf import settings


class ImaggaContentError(Exception):
    pass


class ImaggaAPI(object):
    def __init__(self, key=None, secret=None):
        _key = key if key else settings.IMAGGA_KEY
        _secret = secret if secret else settings.IMAGGA_SECRET
        self.base_url = 'https://api.imagga.com/v1/'

        assert _key is not None and _secret is not None, \
            'Credentials not provided'

        # auth tuple for performing request
        self.auth = (_key, _secret)

    def tagging(self, url=None, **kwargs):
        """
        In the Imagga docs url can be a list up to 5 urls.
        :param url: it is an image url that needs to be "tagged",
        :param kwargs:
            :param content:
            :param language:
            :param verbose:
        :return:
        """
        endpoint_url = self.base_url + 'tagging'
        payload = {}
        if url:
            payload['url'] = url
        payload.update(kwargs)

        r = requests.get(endpoint_url,
                         params=payload, timeout=60, auth=self.auth)

        assert r.status_code == 200

        return r.json()

    def content(self, image_path):
        """ Upload one image and returns its ID."""
        endpoint_url = self.base_url + 'content'
        charset = ascii_letters + digits
        with open(image_path, 'rb') as f:
            # trick for files titled with chinese charset
            filename, ext = os.path.splitext(image_path)

            tmp_name = ''.join([random.choice(charset) for _ in range(32)])
            files = {'image': (tmp_name + ext, f.read())}

            r = requests.post(endpoint_url, auth=self.auth, files=files)
            assert r.status_code == 200
            data = r.json()
            if data['status'] == 'success':
                return data['uploaded'][0]['id']
            else:
                raise ImaggaContentError(data['message'])

    def content_many(self, *paths):
        """ Careful! Do not use it. It uploads many files and
        returns ID`s with file names."""
        endpoint_url = self.base_url + 'content'
        files = {}
        for path in paths:
            files.update({os.path.basename(path): open(path, 'r')})

        r = requests.post(endpoint_url, auth=self.auth, files=files)
        assert r.status_code == 200

        data = r.json()
        # return [i['id'] for i in data['uploaded']]
        return data['uploaded']

    def get_tags_by_filepath(self, image_path, **kwargs):
        content = self.content(image_path)
        return self.tagging(content=content, **kwargs)

if __name__ == '__main__':
    api = ImaggaAPI(key='acc_60524b660772546',
                    secret='b8a7133f5990d04038ce468c7321d82c')

    tag_response = api.get_tags_by_filepath('/home/niklak/repositories/atyichu/back/'
                                            'media/无需过多装饰简洁的纯白色连衣裙就能瞬间体现女人味气质_thumb.jpeg',
                               language='zh_chs')
    print (tag_response)
