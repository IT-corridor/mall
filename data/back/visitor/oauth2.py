from __future__ import unicode_literals

import requests
from django.conf import settings
from urllib import urlencode, quote
from urlparse import urljoin


class WeixinBackend(object):

    authorize = {'url': 'https://open.weixin.qq.com/connect/oauth2/authorize',
                 'extra': {'response_type': 'code',
                           'state': 'STATE#wechat_redirect',
                           'scope': 'snsapi_userinfo, snsapi_base',
                           }
                 }

    access = {
              'url': 'https://api.weixin.qq.com/sns/oauth2/access_token',
              'extra': {'grant_type': 'authorization_code'}
              }

    refresh = {
               'url': 'https://api.weixin.qq.com/sns/oauth2/refresh_token',
               'extra': {'grant_type': 'refresh_token'}
              }
    access_2 = {
        'url': 'https://api.weixin.qq.com/cgi-bin/token',
        'extra': {'grant_type': 'client_credential'}
    }
    user_url = 'https://api.weixin.qq.com/sns/userinfo'

    appid = settings.WEIXIN_APP_ID
    secret = settings.WEIXIN_SECRET

    def get_authorize_uri(self, redirect_uri):
        params = self.authorize['extra']
        params['redirect_uri'] = redirect_uri
        params['appid'] = self.appid
        return urljoin(self.authorize['url'], '?' + self.format_params(params))

    def get_access_token(self, code):

        params = self.access['extra']
        params['code'] = code
        params['appid'] = self.appid
        params['secret'] = self.secret

        response = requests.get(self.access['url'], params=params)
        data = response.json()
        return data

    def get_user_info(self, access_token, openid):
        params = {'access_token': access_token,
                  'openid': openid}

        response = requests.get(self.user_url, params=params)
        response.encoding = 'utf-8'
        data = response.json()
        # data['encoding'] = response.encoding
        return data

    def get_user_basic_info(self, access_token, openid):
        params = {'access_token': access_token,
                  'openid': openid}

        user_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
        response = requests.get(user_url, params=params)
        response.encoding = 'utf-8'
        data = response.json()
        return data

    def refresh_user_credentials(self, refresh_token):
        params = self.refresh['extra']
        params['appid'] = self.appid
        params['refresh_token'] = refresh_token

        response = requests.get(self.refresh['url'], params=params)
        response.encoding = 'utf-8'
        return response.json()

    def format_params(self, param_map, encode=False):
        li = sorted(param_map)
        buff = [(k, quote(param_map[k]) if encode else param_map[k])
                for k in li]
        return '&'.join('{}={}'.format(k, v) for (k, v) in buff)


class WeixinQRBackend(WeixinBackend):
    authorize = {'url': 'https://open.weixin.qq.com/connect/qrconnect',
                 'extra': {'response_type': 'code',
                           'state': 'STATE#wechat_redirect',
                           'scope': 'snsapi_userinfo, snsapi_base',
                           }
                 }

    appid = settings.WEIXIN_QR_APP_ID
    secret = settings.WEIXIN_QR_SECRET
