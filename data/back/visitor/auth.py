from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import Visitor, VisitorExtra


class WeixinBackend(ModelBackend):
    """
    Authenticate with weixin id. Base is "auth.User" model. It is strict.
    """

    def authenticate(self, weixin=None, backend='weixin'):
        try:
            ve = VisitorExtra.objects.select_related('weixin__visitor__user')\
                .get(openid=weixin, backend=backend)
            user = ve.weixin.visitor.user
        except VisitorExtra.DoesNotExist:
            user = None
        return user


class PhoneBackend(ModelBackend):
    """ Authenticate user (visitor) with phone number """
    def authenticate(self, phone=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            if phone:
                visitor = Visitor.objects.get(phone=phone)
                user = visitor.user
                if user.check_password(password):
                    return user
        except Visitor.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
