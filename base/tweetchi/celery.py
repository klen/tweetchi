from __future__ import absolute_import

from celery import Celery
from flask import current_app as app
from twitter import Twitter, OAuth

from ..app import create_app
from .tweetchi import tweetchi


if not app:
    app = create_app()
    ctx = app.test_request_context()
    ctx.push()

celery = Celery('tweetchi')
celery.config_from_object(dict(
    BROKER_URL='redis://localhost:6379/0',
    CELERY_ENABLE_UTC=True,
    CELERY_TIMEZONE=tweetchi.timezone,
    CELERYBEAT_SCHEDULE={
        'tweetchi-beat': {
            'task': 'base.tweetchi.celery.beat',
            'schedule': tweetchi.beat_schedule
        },
        'tweetchi-reply': {
            'task': 'base.tweetchi.celery.reply',
            'schedule': tweetchi.reply_schedule
        },
    }
))


@celery.task(ignore_result=True)
def beat():
    tweetchi.beat()


@celery.task(ignore_result=True)
def reply():
    tweetchi.reply()


@celery.task(ignore_result=True)
def update(message, *args, **kwargs):
    twitter = Twitter(auth=OAuth(*args))
    twitter.statuses.update(status=message, **kwargs)
