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

        from mock import Mock

        tweetchi.update = Mock()
        tweetchi.beat()
        self.assertEqual(tweetchi.stack, [('1 sheep', {'meta': 2})])
        tweetchi.stack = []

        from .timerange import timerange
        from datetime import timedelta, datetime

        # Sleep test
        self.assertFalse(tweetchi.sleep())

        now = datetime.now()
        tweetchi.disable_timerange = map(timerange, [('13:00', '15:30'), (now, now + timedelta(hours=1))])
        self.assertTrue(tweetchi.sleep())

        tweetchi.say(22)
        tweetchi.beat()
        self.assertEqual(tweetchi.stack, [(22, {})])

    def test_timerange(self):
        from .timerange import timerange
        from datetime import datetime, time

        r1 = timerange('15:00', '17:00')
        r2 = timerange((15, 00), (17, 00))
        r3 = timerange(time(23, 0), time(2, 0))
        r4 = timerange(r3)
        self.assertEqual(r1, r2)
        self.assertEqual(r3, r4)
        self.assertTrue(r3)

        d = datetime(2012, 01, 01, 15, 33)
        self.assertTrue(d in r1)

        d = datetime(2012, 01, 01, 0, 33)
        self.assertTrue(d in r3)
