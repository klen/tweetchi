from __future__ import absolute_import

from celery import Celery

from ..app import create_app
from .tweetchi import tweetchi


app = create_app()
celery = Celery('tweetchi')
celery.config_from_object(dict(
    BROKER_URL='redis://localhost:6379/0',
    CELERYBEAT_SCHEDULE={
        'tweetchi-beat': {
            'task': 'base.tweetchi.celery.beat',
            'schedule': tweetchi.beat_tick
        },
        'tweetchi-reply': {
            'task': 'base.tweetchi.celery.reply',
            'schedule': tweetchi.reply_tick
        },
    }
))


@celery.task(ignore_result=True)
def beat():
    tweetchi.beat()


@celery.task(ignore_result=True)
def reply():
    tweetchi.reply()
