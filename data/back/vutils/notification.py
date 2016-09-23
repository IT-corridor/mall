import pusher

from django.conf import settings


def trigger_notification(channel, event, msg, type_, id_, time_):
    print '@@@@@@', channel, event, msg, type_, id_, time_

    p = pusher.Pusher(app_id=settings.PUSHER_APP_ID, key=settings.PUSHER_KEY,
                      secret=settings.PUSHER_SECRET)
    # channel, event, content
    time_ = time_.strftime('%Y-%m-%d %H:%M:%S')
    p.trigger(channel, event, {'message': msg, 'type': type_, 'id': id_, 'time': time_})
