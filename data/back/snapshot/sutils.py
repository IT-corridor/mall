from __future__ import unicode_literals


import hashlib


def check_sign(timestamp, checksum):
    key = "sdlfkj9234kjlnzxcv90123098123asldjk"
    sign = hashlib.md5('{}{}'.format(key, timestamp)).hexdigest()
    if checksum != sign:
        return False
    return True
