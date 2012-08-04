from twitter import oauth_dance, Twitter, TwitterError, OAuth
from datetime import timedelta

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
        self.beat_tick = app.config.get('TWEETCHI_BEAT_TICK', timedelta(seconds=20))
        self.reply_tick = app.config.get('TWEETCHI_REPLAY_TICK', timedelta(seconds=40))

        self.twitter = Twitter(auth=OAuth(self.oauth_token, self.oauth_secret, self.consumer_key, self.consumer_secret))
        self.stack = []

    def dance(self):
        oauth_token, oauth_token_secret = oauth_dance(self.account, self.consumer_key, self.consumer_secret)

        print "OAUTH_TOKEN: %s" % oauth_token
        print "OAUTH_SECRET: %s" % oauth_token_secret

    def update(self, message, **kwargs):
        try:
            self.twitter.statuses.update(status=message, **kwargs)
        except TwitterError, e:
            self.app.logger.info(message)
            self.app.logger.error(e)

    def beat(self):
        tweetchi_beat.send(self)
        stack = self.stack
        print stack
        while stack:
            message, params = stack.pop(0)
            self.update(message, **params)

        self.stack = []

    def reply(self):
        mentions = self.twitter.statuses.mentions(
            since_id=self.since_id,
            count=200)

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
