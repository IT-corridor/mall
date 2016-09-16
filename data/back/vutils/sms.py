from __future__ import unicode_literals
import requests

# MAYBE IT IS USELESS
#curl -d "corpID=800053&srcAddr='1069015929212301'&destAddr=18030200310&msg='hi'&serviceName='YYDB'ownmsgid='232323'" "http://115.182.51.124:7070/thirdPartner/letvqxtmt"


class SMS():
    def __init__(self):
        self.url = 'http://115.182.51.124:7070/thirdPartner/letvqxtmt'


    def send(self, mobile, msg):
        data = {
            #'corpID': '800053',
            'corpID': '800009',
            'srcAddr': '1069015929212301',
            'destAddr': mobile,
            'msg': msg.encode("gbk"),
            'serviceName': 'YYDB',
            'downmsgid': '232323',
        }
        req = requests.post(self.url, data=data)

if __name__ == "__main__":
    a= SMS()
    a.send("18600320375", u"我是中国人")
