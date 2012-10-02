from __future__ import absolute_import

from celery import Celery
from celery.utils.log import get_task_logger
from flask import current_app as app
from twitter import Twitter, OAuth, TwitterError
from functools import wraps
from sqlalchemy.exc import InvalidRequestError

from ..app import create_app
from .models import Status, db
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
        'tweetchi-promote': {
            'task': 'base.tweetchi.celery.promote',
            'schedule': tweetchi.config.get('PROMOTE_SCHEDULE'),
        },
    }
))


def safe_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except InvalidRequestError:
            db.session.rollback()
    return wrapper


@celery.task(ignore_result=True)
@safe_session
def beat():
    " Tweetchi ticker. "

    tweetchi.beat()


@celery.task(ignore_result=True)
@safe_session
def reply():
    " Parse replays. "

    tweetchi.reply()


@celery.task(ignore_result=True)
@safe_session
def promote():
    " Promote account. "

    tweetchi.promote()


@celery.task(ignore_result=True)
def update(message, *args, **kwargs):
    " Async twitter update. "

    twitter = Twitter(auth=OAuth(*args))
    try:
        status = Status.create_from_status(
            twitter.statuses.update(status=message, **kwargs),
            myself=True)
        db.session.add(status)
        db.session.commit()
    except TwitterError, e:
        logger.error(e)


# pymode:lint_ignore=E061
