
RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'redis-cache',
        'DB': 4,
        'DEFAULT_TIMEOUT': 1000,
    },
    'low': {
        'USE_REDIS_CACHE': 'redis-cache',
        'DB': 4,
        'DEFAULT_TIMEOUT': 3000,
    }
}

RQ_EXCEPTION_HANDLERS = ['utils.rq_handlers.retry_handler']