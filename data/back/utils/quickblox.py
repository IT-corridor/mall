# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import operator
import random
import hmac
import json
import requests

from hashlib import sha1


class QuickbloxAPI(object):

    def __init__(self, app_id, auth_key, auth_secret):
        self.app_id = app_id
        self.auth_key = auth_key
        self.auth_secret = auth_secret

        self.password = 'atyichu@3212'

    def get_token(self):
        """

        :param user:  A JSON STRING WITH LOGIN
        """
        url = 'https://api.quickblox.com/session.json'
        nonce = str(random.randint(1, 10000))
        timestamp = str(int(time.time()))

        payload = {
            'application_id': self.app_id,
            'auth_key': self.auth_key,
            'timestamp': timestamp,
            'nonce': nonce,
        }

        signature = self._get_signature(payload)
        payload['signature'] = signature

        r = requests.post(url, json=payload)
        assert r.status_code == 201

        return r.json()['session']['token']

    def _get_signature(self, data):
        """ Write a comment """
        sorted_data = sorted(data.items(), key=operator.itemgetter(0))
        s = '&'.join('{}={}'.format(k, v) for k, v in sorted_data)
        return hmac.new(str(self.auth_secret), str(s), sha1).hexdigest()

    def sign_up(self, login, full_name, token):
        """
        Login must be unique, And it will be a user PK
        """
        if len(full_name) < 3:
            full_name += '_' * (3 - len(full_name))
        url = 'http://api.quickblox.com/users.json'
        headers = {"QB-Token": token}

        payload = {
            'user': {
                'login': 'at' + str(login),
                'password': self.password,
                'full_name': full_name
            }
        }

        r = requests.post(url=url, headers=headers, json=payload)
        print r.text
        assert r.status_code == 201
        return r.json()['user']['login']

    def sign_in(self, login, token):
        url = 'http://api.quickblox.com/login.json'
        headers = {"QB-Token": token}
        payload = {'login': login, 'password': self.password}

        r = requests.post(url=url, headers=headers, json=payload)
        assert r.status_code == 202

    def sign_out(self, token):
        url = 'http://api.quickblox.com/login.json'
        headers = {"QB-Token": token}
        r = requests.delete(url=url, headers=headers)
        assert r.status_code == 200

    def destroy_session(self, token):
        url = 'http://api.quickblox.com/session.json'
        headers = {"QB-Token": token}
        r = requests.delete(url=url, headers=headers)
        assert r.status_code == 200

if __name__ == '__main__':
    app_id = '47235'
    auth_key = 'bMaMr7rX86sbGqN'
    auth_secret = 'YbetO6dx7fDb7Yn'
    api = QuickbloxAPI(app_id, auth_key, auth_secret)
    token = api.get_token()
    # 来去
    print token

    login = api.sign_up(8, 'JonSnowц', token)
    api.sign_in(login, token)
    api.sign_out(token)
    api.destroy_session(token)