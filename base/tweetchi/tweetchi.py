from __future__ import absolute_import

from datetime import timedelta

from twitter import oauth_dance, Twitter, TwitterError, OAuth
from celery.schedules import crontab

from ..ext import cache
from .signals import tweetchi_beat, tweetchi_reply
from .types import Status


def twitter_error(func):
    " Catch twitter errors. "

    def wrapper(tweetchi, *args, **kwargs):
        try:
            return func(tweetchi, *args, **kwargs)
        except TwitterError, e:
            tweetchi.app.logger.error(str(e))
    return wrapper


class Tweetchi(object):

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.config = dict(
            ACCOUNT=app.config.get('TWEETCHI_ACCOUNT', ''),
            CONSUMER_KEY=app.config.get('TWEETCHI_CONSUMER_KEY', ''),
            CONSUMER_SECRET=app.config.get('TWEETCHI_CONSUMER_SECRET', ''),
            OAUTH_TOKEN=app.config.get('TWEETCHI_OAUTH_TOKEN', ''),
            OAUTH_SECRET=app.config.get('TWEETCHI_OAUTH_SECRET', ''),
            BEAT_SCHEDULE=app.config.get(
                'TWEETCHI_BEAT_SCHEDULE', crontab(minute='*/60')),
            REPLAY_SCHEDULE=app.config.get(
                'TWEETCHI_REPLAY_SCHEDULE', timedelta(seconds=30)),
            TIMEZONE=app.config.get('TWEETCHI_TIMEZONE', 'UTC'),
            BROKER_URL=app.config.get('BROKER_URL'),
        )

        self.twitter = Twitter(
            auth=OAuth(
                self.config.get(
                    'OAUTH_TOKEN'), self.config.get('OAUTH_SECRET'),
                self.config.get('CONSUMER_KEY'), self.config.get('CONSUMER_SECRET')))
        self.stack = []

        if not hasattr(self.app, 'extensions'):
            self.app.extensions = dict()

        self.app.extensions['tweetchi'] = self

    @twitter_error
    def dance(self):
        " Get OAauth params. "

        oauth_token, oauth_secret = oauth_dance(
            self.config.get('ACCOUNT'), self.config.get('CONSUMER_KEY'), self.config.get('CONSUMER_SECRET'))

        self.app.logger.info("OAUTH_TOKEN: %s", oauth_token)
        self.app.logger.info("OAUTH_SECRET: %s", oauth_secret)

    @twitter_error
    def update(self, message, async=False, **kwargs):
        " Update twitter status. "

        self.app.logger.info('Tweetchi: "%s"' % message)

        if async:
            from .celery import update as cupdate
            return cupdate.delay(message,
                                 self.config.get('OAUTH_TOKEN'),
                                 self.config.get('OAUTH_SECRET'),
                                 self.config.get('CONSUMER_KEY'),
                                 self.config.get('CONSUMER_SECRET'), **kwargs)

        status = self.twitter.statuses.update(status=message, **kwargs)
        return Status(status)

    @twitter_error
    def mentions(self):
        " Get account mentions. "

        statuses = self.twitter.statuses.mentions(
            since_id=self.since_id,
            count=200)
        return map(Status, statuses)

    def beat(self):
        " Updates twitter beat. "

        updates = []

        # Send updates
        stack = self.stack
        while stack:
            message, params = stack.pop(0)
            meta = params.pop('meta', None)
            status = self.update(message, **params)
            updates.append((status, meta))

        # Clean queue
        self.stack = []

        # Send signal
        tweetchi_beat.send(self, updates=updates)

    def reply(self):
        " Parse replays twitter beat. "
        statuses = sorted(self.mentions() or [])
        if statuses:
            self.since_id = statuses[-1].id
        tweetchi_reply.send(self, mentions=statuses)

    @property
    def since_id(self):
        " Get last parst tweet_id from redis. "
        return cache.get('tweetchi.since_id.%s' % self.config.get('ACCOUNT')) or '1'

    @since_id.setter
    def since_id(self, value):
        " Save last parsed tweet_id to redis. "
        try:
            cache.cache._client.set('tweetchi.since_id.%s' % self.config.get('ACCOUNT'), value)
        except AttributeError:
            cache.set('tweetchi.since_id.%s' % self.config.get('ACCOUNT'), value)

    @property
    def stack(self):
        return cache.get('tweetchi.stack.%s' % self.config.get('ACCOUNT')) or []

    @stack.setter
    def stack(self, value):
        cache.set('tweetchi.stack.%s' % self.config.get('ACCOUNT'), value)

    def say(self, value, **params):
        stack = self.stack
        stack.append((value, params))
        self.stack = stack


tweetchi = Tweetchi()
