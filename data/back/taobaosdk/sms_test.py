# -*- coding: utf-8 -*-
import top.api

appkey = '23438643'
secret = '785f1713c9472a73596336a9f5e3eeeb'
url = 'http://gw.api.tbsandbox.com/router/rest'

req = data.back.taobaosdk.top.api.AlibabaAliqinFcSmsNumSendRequest(url, 80)
req.set_app_info(top.appinfo(appkey, secret))

req.extend = "123456"
req.sms_type = "normal"
req.sms_free_sign_name = "阿里大于"
req.sms_param = "{\"code\":\"1234\",\"product\":\"alidayu\"}"
req.rec_num = "13521405982"
req.sms_template_code = "SMS_585014"
resp = req.getResponse()
print(resp)
