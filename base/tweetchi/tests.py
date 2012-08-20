from ..core.tests import FlaskTest
from ..ext import cache
from .signals import tweetchi_beat, tweetchi_reply
from .tweetchi import tweetchi, Status, db


class TweetchiTest(FlaskTest):

    def setUp(self):
        super(TweetchiTest, self).setUp()
        cache.cache.clear()
        tweetchi.stack = []
        tweetchi_beat._clear_state()
        tweetchi_reply._clear_state()

    def test_tweetchi(self):
        " Test twetchi extension. "

        # Check tweetchi app initialization
        self.assertEqual(tweetchi.app, self.app)

        # Check the initial value of since_id
        self.assertEqual(tweetchi.since_id, None)

        # Check since_id setup
        tweetchi.since_id = 143
        self.assertEqual(tweetchi.since_id, 143)

        # Check work with stack
        tweetchi.say(1)
        self.assertEqual(tweetchi.stack, [(1, {})])
        tweetchi.say(2)
        self.assertEqual(tweetchi.stack, [(1, {}), (2, {})])

        def beat(tw, updates=None):
            meta = updates and updates[-1] and updates[-1][1] or 1
            tw.say('%s sheep' % meta, meta=meta + 1)

        tweetchi_beat.connect(beat)

        from mock import Mock

        tweetchi.update = Mock()
        tweetchi.beat()
        self.assertEqual(tweetchi.stack, [('1 sheep', {'meta': 2})])
        tweetchi.stack = []

        tweetchi_beat.disconnect(beat)

        tweetchi.say(22)
        tweetchi.beat()
        self.assertFalse(tweetchi.stack)

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

    def test_replays(self):
        from mock import Mock

        tweetchi.mentions = Mock(return_value=[Status(
            id_str='10',
            screen_name='dummy',
            created_at='Tue Jul 13 17:38:21 +0000 2010',
            in_reply_id_str='10',
            text='test'),
        ])

        mock = Mock(name='test')

        def reply(*args, **kwargs):
            mock(*args, **kwargs)

        tweetchi_reply.connect(reply)

        tweetchi.reply()
        self.assertFalse(mock.call_count)
        self.assertEqual(tweetchi.since_id, '10')

        tweetchi.reply()
        self.assertEqual(mock.call_count, 1)

        tweetchi.mentions = Mock(return_value=[])
        tweetchi.reply()
        self.assertEqual(mock.call_count, 1)

    def test_status(self):
        status = Status.create_from_status(
            dict(
                id_str='10',
                user=dict(screen_name='poliglot'),
                created_at='Tue Jul 13 17:38:21 +0000 2010',
                text='test'),
            myself=True
        )
        db.session.add(status)
        db.session.commit()
        self.assertEqual(status.created_at.day, 13)
        self.assertTrue(status.id)

        status = Status.create_from_status(
            dict(
                id_str='14',
                in_reply_to_status_id_str='10',
                user=dict(id_str='10', screen_name='honor'),
                created_at='Tue Jul 13 17:38:21 +0000 2010',
                text='text'))
        db.session.add(status)
        db.session.commit()
        self.assertFalse(status.myself)

        self.assertEqual(tweetchi.since_id, '14')
