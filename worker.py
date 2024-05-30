from kombu import Queue

from config import conf

from infrastructure.celery.main import get_celery_factory


# Celery is implemented only, currently unused
# Todo: use for integration.api webhook notifier
app = get_celery_factory(__name__, conf.celery)

app.conf.update(
    task_queues=(
        Queue('webdriver'),
    ),
    task_routes={
        'infrastructure.tasks.my_task': {'queue': 'webdriver'}
    },
    task_default_queue='default',
    task_default_routing_key='default'
)

app.autodiscover_tasks(['infrastructure'])

# usage @example
# infrastructure.tasks.py
# @shared_task
# def my_task():
#   return True

# Then
# app.send_task('infrastructure.tasks.my_task')