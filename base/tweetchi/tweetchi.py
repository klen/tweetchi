from datetime import timedelta

from twitter import oauth_dance, Twitter, TwitterError, OAuth

from ..ext import cache
from .signals import tweetchi_beat, tweetchi_reply


class Tweetchi(object):

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        self.account = app.config.get('TWEETCHI_ACCOUNT', '')
        self.consumer_key = app.config.get('TWEETCHI_CONSUMER_KEY', '')
        self.consumer_secret = app.config.get('TWEETCHI_CONSUMER_SECRET', '')
        self.oauth_token = app.config.get('TWEETCHI_OAUTH_TOKEN', '')
        self.oauth_secret = app.config.get('TWEETCHI_OAUTH_SECRET', '')
        self.beat_schedule = app.config.get(
            'TWEETCHI_BEAT_SCHEDULE', timedelta(seconds=20))
        self.reply_schedule = app.config.get(
            'TWEETCHI_REPLAY_SCHEDULE', timedelta(seconds=40))
        self.timezone = app.config.get('TWEETCHI_TIMEZONE', 'UTC')

        self.twitter = Twitter(auth=OAuth(self.oauth_token, self.oauth_secret,
                               self.consumer_key, self.consumer_secret))
        self.stack = []

        if not hasattr(self.app, 'extensions'):
            self.app.extensions = dict()

        self.app.extensions['tweetchi'] = self

    def dance(self):
        oauth_token, oauth_token_secret = oauth_dance(
            self.account, self.consumer_key, self.consumer_secret)

        print "OAUTH_TOKEN: %s" % oauth_token
        print "OAUTH_SECRET: %s" % oauth_token_secret

    def update(self, message, async=False, **kwargs):
        " Post twitter status. "
        self.app.logger.info('Tweetchi: "%s"' % message)
        if async:
            from .celery import update as cupdate
            return cupdate.delay(
                message, self.oauth_token, self.oauth_secret, self.consumer_key, self.consumer_secret, **kwargs)

        try:
            return self.twitter.statuses.update(status=message, **kwargs)
        except TwitterError, e:
            self.app.logger.info(message)
            self.app.logger.error(e)

    def mentions(self):
        try:
            return self.twitter.statuses.mentions(
                since_id=self.since_id,
                count=200)

        except TwitterError, e:
            self.app.logger.error(e)

    def beat(self):
        " Updates twitter beat. "

        updates = []

        # Send updates
        stack = self.stack
        while stack:
            message, params = stack.pop(0)
            meta = params.pop('meta', None)
            self.app.logger.info(message)
            response = self.update(message, **params)
            updates.append((response, meta))

        # Clean queue
        self.stack = []

        # Send signal
        tweetchi_beat.send(self, updates=updates)

    def reply(self):
        " Parse replays twitter beat. "

        mentions = self.mentions()

        if not mentions:
            return False

        mentions = sorted(mentions, key=lambda m: m['id_str'])
        tweetchi_reply.send(self, mentions=mentions)
        self.since_id = mentions[-1]['id_str']

    @property
    def since_id(self):
        return cache.get('tweetchi.since_id') or 100

    @since_id.setter
    def since_id(self, value):
        cache.set('tweetchi.since_id', value, timeout=3600 * 24 * 30)

    @property
    def stack(self):
        return cache.get('tweetchi.stack') or []

    @stack.setter
    def stack(self, value):
        cache.set('tweetchi.stack', value)

    def say(self, value, **params):
        stack = self.stack
        stack.append((value, params))
        self.stack = stack


tweetchi = Tweetchi()
