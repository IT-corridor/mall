import django_rq


def retry_handler(job, exc_type, exc_value, trace):
    """ If task has fail we put it in the low priority queue."""

    job.meta.setdefault('failures', 0)
    job.meta['failures'] += 1
    if job.meta['failures'] > 3:

        worker = django_rq.get_worker(job.origin)
        worker.move_to_failed_queue(job, exc_type, exc_value, trace)
        return True

    queue = django_rq.get_queue('low')
    job.timeout = queue._default_timeout
    queue.enqueue_job(job)

    return False
