# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import time

import hashlib
import requests
import json
import urllib2
import datetime
import os
import cgi

from django.conf import settings


def md5(s):
    m = hashlib.md5(s)
    return m.hexdigest()


def push_unicast(device_token, text):
    timestamp = int(time.time() * 1000)
    method = 'POST'
    url = 'http://msg.umeng.com/api/send'

    params = {
        'appkey': settings.UMENG_APP_KEY,
        'timestamp': timestamp,
        'device_tokens': device_token,
        # "production_mode":"false",
        'type': 'unicast',
        "payload": {
            "display_type": "message",
            "body": {
                "custom": text
            }
        },
        # "policy":
        # {
        #    "expire_time":"%s"%(datetime.datetime.now())
        # },
        "description": "жµ‹иЇ•еЌ•ж’­ж¶€жЃЇ-Android"
    }

    post_body = json.dumps(params)
    sign = md5('%s%s%s%s' % (
    method, url, post_body, settings.UMENG_APP_MASTER_SECRET))
    success_info = ""

    try:
        r = urllib2.urlopen(url + '?sign=' + sign, data=post_body)
        success_info = r.read()
        print success_info
    except urllib2.HTTPError, e:
        print e.reason, e.read()
    except urllib2.URLError, e:
        print e.reason
    return post_body, success_info
