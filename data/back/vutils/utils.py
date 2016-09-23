from __future__ import unicode_literals

import string
import random
import re
import calendar
import datetime


# IT LOOKS LIKE BOTH FUNCTIONS ARE USELESS
def generate_number_random(count):
    return ''.join(random.choice(string.digits) for _ in range(count))


def is_mobile(mobile):
    if re.match('^(1[34578]\d{9})$', mobile.strip()) is None:
        return False
    return True


def get_last_day_of_month(year, month):
    """
    Get the available last day of month for dashboard
    :param year: integer e.g) 1981
    :param month: integer e.g) 3, 12
    :return: valid value for past
    """
    today = datetime.datetime.now().date()
    if year > today.year:
        return 0
    elif year == today.year and month > today.month:
        return 0
    elif year == today.year and month == today.month:
        return today.day
    else:
        return calendar.monthrange(year, month)[1]


def get_nickname(user):
    if hasattr(user, 'vendor'):
        return user.vendor.store.name or user.vendor.store.brand_name
    elif hasattr(user, 'visitor'):
        return user.visitor.username or user.username