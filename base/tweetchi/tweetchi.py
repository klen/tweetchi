from twitter import oauth_dance, Twitter, TwitterError, OAuth
from datetime import timedelta

from ..ext import cache
from .signals import tweetchi_beat, tweetchi_reply


class Tweetchi():

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
        self.beat_tick = app.config.get('TWEETCHI_BEAT_TICK', timedelta(minutes=10))
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
            self.app.loger.error(e)

    def beat(self):
        tweetchi_beat.send(self, app=self)
        while self.stack:
            message, params = self.stack.pop(0)
            self.update(message, **params)

    def reply(self):
        mentions = self.twitter.statuses.mentions(
            since_id=self.since_id,
            count=200)

        if not mentions:
            return False

        mentions = sorted(mentions, key=lambda m: m['id'])
        tweetchi_reply.send(self, app=self, mentions=mentions)

    @property
    def since_id(self):
        return cache.get('tweetchi.since_id') or 100


tweetchi = Tweetchi()
