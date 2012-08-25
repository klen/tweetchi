from __future__ import absolute_import

from datetime import timedelta
from random import choice

from celery.schedules import crontab
from twitter import oauth_dance, Twitter, TwitterError, OAuth

from ..ext import cache, db
from .models import Status
from .signals import tweetchi_beat, tweetchi_reply
from .utils import get_new_followers, as_tuple


def twitter_error(func):
    " Catch twitter errors. "

    def wrapper(tw, *args, **kwargs):
        try:
            return func(tw, *args, **kwargs)
        except TwitterError, e:
            tw.app.logger.error(str(e))
    return wrapper


class Api(object):

    def __init__(self):
        self.twitter_api = None
        self.twitter_search = Twitter(domain='search.twitter.com')

    @twitter_error
    def search(self, query, **params):
        if isinstance(query, unicode):
            query = query.encode('utf-8')
        return self.twitter_search.search(q=query, **params)

    @twitter_error
    def follow(self, ids, limit=10):
        " Follow on user. "
        for user_id in as_tuple(ids):
            self.twitter_api.friendships.create(user_id=user_id)
            limit -= 1
            if not limit:
                return True

    @twitter_error
    def mentions(self, since_id=None):
        " Get account mentions and save in db. "

        params = dict(count=200)
        if since_id:
            params['since_id'] = since_id

        mentions = sorted(map(
            Status.create_from_status,
            self.twitter_api.statuses.mentions(**params)))
        db.session.add_all(mentions)
        db.session.commit()

        return mentions

    @twitter_error
    def update(self, message, async=False, **kwargs):
        " Update twitter status and save it in db. "

        self.app.logger.info('Tweetchi: "%s"' % message)

        if not async:

            status = Status.create_from_status(
                self.twitter_api.statuses.update(status=message, **kwargs),
                myself=True)

            db.session.add(status)
            db.session.commit()

            return status

        from .celery import update as cupdate
        cupdate.delay(message,
                      self.config.get('OAUTH_TOKEN'),
                      self.config.get('OAUTH_SECRET'),
                      self.config.get('CONSUMER_KEY'),
                      self.config.get('CONSUMER_SECRET'), **kwargs)


class Tweetchi(Api):

    def __init__(self, app=None):
        " Init tweetchi. "

        super(Tweetchi, self).__init__()

        self.app = None
        self.config = dict()
        self.key = 'tweetchi'
        if app:
            self.init_app(app)

    def init_app(self, app):
        " Setup settings and create twitter client. "

        self.app = app
        self.config.update(
            dict(
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
                PROMOTE_SCHEDULE=app.config.get(
                    'TWEETCHI_PROMOTE_SCHEDULE', timedelta(hours=12)),
                PROMOTE_QUERIES=app.config.get(
                    'TWEETCHI_PROMOTE_QUERIES', []),
                PROMOTE_REACTIONS=app.config.get(
                    'TWEETCHI_PROMOTE_REACTIONS', []),
                PROMOTE_LIMIT=app.config.get(
                    'TWEETCHI_PROMOTE_LIMIT', 4),
                PROMOTE_AUTO_FOLLOW=app.config.get(
                    'TWEETCHI_PROMOTE_AUTO_FOLLOW', True),
            )
        )

        self.twitter_api = Twitter(
            auth=OAuth(
                self.config.get(
                    'OAUTH_TOKEN'), self.config.get('OAUTH_SECRET'),
                self.config.get('CONSUMER_KEY'), self.config.get('CONSUMER_SECRET')))
        self.stack = []
        self.key = "tweetchi.%s" % self.config.get('ACCOUNT')

        if not hasattr(self.app, 'extensions'):
            self.app.extensions = dict()

        self.app.extensions['tweetchi'] = self

    def beat(self):
        " Send signal and psrse self stack. "

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
        " Parse replays from twitter and send signal. "

        since_id = self.since_id
        mentions = self.mentions(since_id) or []

        if mentions:
            self.since_id = mentions[-1].id_str

            if since_id:
                tweetchi_reply.send(self, mentions=mentions)

    def promote(self):
        queries = self.config.get('PROMOTE_QUERIES')
        reactions = self.config.get('PROMOTE_REACTIONS')
        limit = self.config.get('PROMOTE_LIMIT')
        auto_follow = self.config.get('PROMOTE_AUTO_FOLLOW')
        account = self.config.get('ACCOUNT')

        if auto_follow:
            new_followers = get_new_followers(self, account)
            self.follow(new_followers, limit=limit)

        if not queries or not reactions:
            return False

        # Get search results
        for query in queries:
            result = self.search(query)['results']
            promoted = db.session.query(Status.in_reply_to_screen_name).\
                distinct(Status.in_reply_to_screen_name).\
                filter(Status.in_reply_to_screen_name.in_(s['from_user'] for s in result),
                       Status.myself == True).\
                all()

            for s in filter(lambda s: not s['from_user'] in promoted, result):
                limit -= 1
                self.update(
                    "@%s %s" % (s['from_user'], choice(reactions)),
                    async=True,
                    in_reply_to_status_id=s['id_str']
                )
                if not limit:
                    return True

    @twitter_error
    def dance(self):
        " Get OAauth params. "

        oauth_token, oauth_secret = oauth_dance(
            self.config.get('ACCOUNT'), self.config.get('CONSUMER_KEY'), self.config.get('CONSUMER_SECRET'))

        self.app.logger.info("OAUTH_TOKEN: %s", oauth_token)
        self.app.logger.info("OAUTH_SECRET: %s", oauth_secret)

    @property
    def since_id(self):
        " Get last id_str from mentions. "

        key = "%s.since_id" % self.key

        since_id = cache.get(key)
        if not since_id:
            last = Status.query.filter(Status.myself == False).\
                order_by(Status.id_str.desc()).first()
            self.since_id = since_id = last and last.id_str or last

        return since_id

    @since_id.setter
    def since_id(self, value):
        " Save last parsed tweet_id to redis. "

        key = "%s.since_id" % self.key
        cache.set(key, value, timeout=600)

    @property
    def stack(self):
        key = "%s.stack" % self.key
        return cache.get(key) or []

    @stack.setter
    def stack(self, value):
        key = "%s.stack" % self.key
        cache.set(key, value)

    def say(self, value, **params):
        stack = self.stack
        stack.append((value, params))
        self.stack = stack


tweetchi = Tweetchi()


# pymode:lint_ignore=E0611,E712
