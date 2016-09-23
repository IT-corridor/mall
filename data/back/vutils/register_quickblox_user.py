import time
import random
import hmac
import urllib
import json
import requests

from hashlib import sha1
from vutils.utils import get_nickname


def get_qb_token():
    nonce = str(random.randint(1, 10000))
    timestamp = str(int(time.time()))

    application_id = '46077'
    auth_key = 'F9FMK5hzzPsuO26'
    auth_secret = 'uApjQ6BZrPg-Gcq'

    signature_raw_body = ("application_id=" + application_id + "&auth_key=" + auth_key +
                          "&nonce=" + nonce + "&timestamp=" + timestamp)

    signature = hmac.new(auth_secret, signature_raw_body, sha1).hexdigest()

    params = urllib.urlencode({'application_id': application_id,
                               'auth_key': auth_key,
                               'timestamp': timestamp,
                               'nonce': nonce,
                               'signature': signature})

    url = 'https://api.quickblox.com/session.json'
    res = requests.post(url=url, data=params)
    res_json = res.json()

    return res_json['session']['token']


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def user_signup_qb(instance):
    if hasattr(instance, 'user'):
        user = instance.user
    else:
        user = instance.vendor.user
    full_name = get_nickname(user)
    login = user.username.replace(' ', '')

    if not full_name:
        print login, '$$$ Not vendor or visitor'
        return

    token = get_qb_token()
    url = 'http://api.quickblox.com/users.json'
    header = {"QB-Token": token,
              "Content-Type": "application/json"}

    if not is_ascii(full_name) and len(full_name) < 3:
        full_name += '_' * (3-len(full_name))

    if not is_ascii(user.username):
        login = user.username.encode("hex")

    if full_name:
        params = {'user': {
            'login': login,
            'password': 'atyichu@3212',
            'full_name': full_name}}

        res = requests.post(url=url, headers=header, data=json.dumps(params))
        print login, '@@', full_name, '===', res.json()
