
RQ_QUEUES = {
    'default': {
        'HOST': 'pub-redis-14525.us-east-1-3.3.ec2.garantiadata.com',
        'PORT': '14525',
        'PASSWORD': 'test',
        'DB': 0,
        'DEFAULT_TIMEOUT': 1000,
    },
    'low': {
        'HOST': 'pub-redis-14525.us-east-1-3.3.ec2.garantiadata.com',
        'PORT': '14525',
        'PASSWORD': 'test',
        'DB': 0,
        'DEFAULT_TIMEOUT': 3000,
    },
}

RQ_EXCEPTION_HANDLERS = ['utils.rq_handlers.retry_handler']
