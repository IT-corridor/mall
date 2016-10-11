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

    def get_token(self, user=None):
        """
        :param user:  A JSON STRING WITH LOGIN AND PASSWORD
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
        if user is not None and isinstance(user, str):
            payload['user'] = user
        signature = self._get_signature(payload)
        payload['signature'] = signature

        r = requests.post(url, json=payload)
        assert r.status_code == 201, r.text

        return r.json()['session']['token']

    def _get_signature(self, data):
        """ Write a comment """
        sorted_data = sorted(data.items(), key=operator.itemgetter(0))
        s = '&'.join('{}={}'.format(k, v) for k, v in sorted_data)
        return hmac.new(str(self.auth_secret), str(s), sha1).hexdigest()

    def sign_up(self, login, full_name, password, token):
        """
        Login must be unique, And it will be a user PK
        """
        cleaned_name = self.reformat_full_name(full_name)

        url = 'http://api.quickblox.com/users.json'
        headers = {"QB-Token": token}

        payload = {
            'user': {
                'login': 'aty' + str(login),
                'password': password,
                'full_name': cleaned_name,
                'custom_data': full_name
            }
        }

        r = requests.post(url=url, headers=headers, json=payload)

        assert r.status_code == 201, r.text
        return r.json()

    def reformat_full_name(self, full_name):
        if len(full_name) < 3:
            full_name += '_' * (3 - len(full_name))
        return full_name

    def sign_in(self, login, password, token):
        url = 'http://api.quickblox.com/login.json'
        headers = {"QB-Token": token}
        payload = {'login': login, 'password': password}

        r = requests.post(url=url, headers=headers, json=payload)
        assert r.status_code == 202
        return r.json()

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

    def update_user_data(self, qid, user_data, token):
        """ user_data, expected a dict """
        url = 'http://api.quickblox.com/users/{}.json'.format(qid)
        if 'full_name' in user_data:
            user_data['custom_data'] = user_data['full_name']
            user_data['full_name'] = self.reformat_full_name(
                user_data['full_name'])

        headers = {"QB-Token": token}
        payload = {'user': user_data}

        r = requests.put(url=url, headers=headers, json=payload)
        assert r.status_code == 200
        return r.json()

if __name__ == '__main__':
    app_id = '47642'
    auth_key = 'cPbb6XAAEgYwmF5'
    auth_secret = 'qcwkUf5dD73gLDS'
    api = QuickbloxAPI(app_id, auth_key, auth_secret)
    token = api.get_token()
    # 来去
    # print token
    # password = 'asd112345!!'
    # #login = api.sign_up('woop1', 'Starky7', password, token)['user']['login']
    #
    # login = api.sign_in('atywoop1', password, token)
    # api.update_user_data(login['user']['id'], {'full_name': 'Starky the Great'}, token)
    #
    api.sign_out(token)
    api.destroy_session(token)
