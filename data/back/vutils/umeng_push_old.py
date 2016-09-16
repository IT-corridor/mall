# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import time

import hashlib
import requests
import json
import urllib2
import datetime

#{"appkey": "56f3b94267e58e49270019e7", "production_mode": "false",
# "description": "testaaa", "type": "unicast",
#"payload": {"display_type": "message", "body": {"custom": "aaabbb"}},
# "policy": {"expire_time": "2016-04-12 17:07:55"},
# "device_tokens": "AjzbcO4OoVNsKfYPdSoilaohG3pjlfPCBdhpXGaBiGMs"}


def md5(s):
    m = hashlib.md5(s)
    return m.hexdigest()


def push_unicast(appkey, app_master_secret, device_token, text):
    timestamp = int(time.time() * 1000 )
    method = 'POST'
    url = 'http://msg.umeng.com/api/send'
    params = {'appkey': appkey,
              'timestamp': timestamp,
              'device_tokens': device_token,
              "production_mode":"false",
              "description":"testaaa",
              'type': 'unicast',
                "payload":
                {
                    "display_type": "message",
                    "body":
                    {
                    "custom":"%s"%text
                    }
                },
                #"policy":
                #{
                #    "expire_time":"%s"%(datetime.datetime.now())
                #},
                "description": "测试单播消息-Android"
             }


    post_body = json.dumps(params)
    sign = md5('%s%s%s%s' % (method,url,post_body,app_master_secret))
    success_info = ""
    try:
        r = urllib2.urlopen(url + '?sign='+sign, data=post_body)
        success_info = r.read()
        print success_info
    except urllib2.HTTPError,e:
        print e.reason,e.read()
    except urllib2.URLError,e:
        print e.reason
    return post_body, success_info

if __name__ == '__main__':
    """
    {"appkey":"56f3b94267e58e49270019e7","production_mode":"false","description":"testaaa","type":"unicast","payload":{"display_type":"message","body":{"custom":"aaabbb"}},"policy":{"expire_time":"2016-04-12 17:07:55"},"device_tokens":"AjzbcO4OoVNsKfYPdSoilaohG3pjlfPCBdhpXGaBiGMs"}
    """
    appkey = 'your appkey'
    app_master_secret = 'your app_master_secret'
    device_token = 'your device_token'

    push_unicast(appkey, app_master_secret, device_token)
