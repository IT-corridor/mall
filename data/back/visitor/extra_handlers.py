import random
from django.core.cache import caches
from django.core.mail import mail_admins


class PendingUserVault(object):
    # TODO: Implement in the future key for the tokens
    def __init__(self):

        self.cache = caches['pending']

    def add_by_sessionid(self, request, user):
        """ Place user in the vault,
            returns a code
         """
        if request.session.session_key is None:
            request.session.cycle_key()
        sessionid = request.session.session_key
        code = random.randint(1000, 9999)
        mail_admins('Verification code', 'Code: {}'.format(code))
        self.cache.set(sessionid, (code, user), 180)
        return code

    def get_by_sessionid(self, sessionid, code):
        """ Get user by sessionid and code"""
        try:
            check_code, user = self.cache.get(sessionid)
        except TypeError:
            return
        if int(code) == check_code:
            self.cache.delete(sessionid)
            return user
        return


class PhonesVault(object):
    def __init__(self):

        self.pending_cache = caches['pending_phones']
        self.verify_cache = caches['verify_phones']

    def add_by_sessionid(self, request, phone):
        """ Put phone in the vault,
            returns a code
         """
        if request.session.session_key is None:
            request.session.cycle_key()
        sessionid = request.session.session_key
        code = random.randint(1000, 9999)
        mail_admins('Verification code', 'Code: {}'.format(code))
        self.pending_cache.set(sessionid, (code, phone), 180)
        return code

    def get_pending_by_sessionid(self, sessionid, code):
        """ Get user by sessionid and code, then replace it
        to the verify_cache"""
        try:
            check_code, phone = self.pending_cache.get(sessionid)
        except TypeError:
            return
        if int(code) == check_code:
            self.pending_cache.delete(sessionid)
            self.verify_cache.set(sessionid, phone, 180)
            return phone
        return

    def get_verify_by_sessionid(self, sessionid):
        """ Returns phone that have passed verification """
        phone = self.verify_cache.get(sessionid)
        # self.verify_cache.delete(sessionid)
        return phone
