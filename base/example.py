from .ext import cache


def register_app(app):
    " Configure application. "

    from .tweetchi.signals import tweetchi_beat, tweetchi_reply
    tweetchi_beat.connect(beat)
    tweetchi_reply.connect(reply)


def beat(tweetchi):
    test = cache.get('example.test') or 0
    tweetchi.say('%s sheep' % test)
    cache.set('example.test', test + 1)


def reply(tweetchi, mentions=None):
    for m in mentions:
        tweetchi.update(
            '@%s hey, %s sheep waz here' % (m['user']['screen_name'], cache.get('example.test')),
            in_reply_to_status_id=m['id_str'])
