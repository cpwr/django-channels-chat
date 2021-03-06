from celery import Celery

# set the default Django settings module for the 'celery' program.
from django.conf import settings


app = Celery('chat', backend='redis://', broker='redis://redis:6379/0')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
