from flask_testing import TestCase

from ..app import create_app
from ..config import test
from ..ext import db


class TweetchiTest(TestCase):

    def create_app(self):
        return create_app(test)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_tweetchi(self):
        from ..ext import cache

        from .tweetchi import tweetchi
        self.assertEqual(tweetchi.app, self.app)

        tweetchi.since_id = 143
        self.assertEqual(tweetchi.since_id, 143)
        self.assertEqual(cache.get('tweetchi.since_id'), 143)

        cache.set('tweetchi.stack', [])
        tweetchi.say(1)
        self.assertEqual(tweetchi.stack, [(1, {})])

        tweetchi.say(2)
        self.assertEqual(tweetchi.stack, [(1, {}), (2, {})])
