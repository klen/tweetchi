from __future__ import absolute_import

from celery import Celery
from celery.utils.log import get_task_logger
from flask import current_app as app
from twitter import Twitter, OAuth, TwitterError

from ..app import create_app
from .tweetchi import tweetchi


logger = get_task_logger('tweetchi')


if not app:
    app = create_app()
    ctx = app.test_request_context()
    ctx.push()

celery = Celery('tweetchi')
celery.config_from_object(dict(
    BROKER_URL=tweetchi.config.get('BROKER_URL'),
    CELERY_ENABLE_UTC=True,
    CELERY_TIMEZONE=tweetchi.config.get('TIMEZONE'),
    CELERYBEAT_SCHEDULE={
        'tweetchi-beat': {
            'task': 'base.tweetchi.celery.beat',
            'schedule': tweetchi.config.get('BEAT_SCHEDULE'),
        },
        'tweetchi-reply': {
            'task': 'base.tweetchi.celery.reply',
            'schedule': tweetchi.config.get('REPLAY_SCHEDULE'),
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
    try:
        twitter.statuses.update(status=message, **kwargs)
    except TwitterError, e:
        logger.error(e)
