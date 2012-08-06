def register_app(app):
    " Configure application. "

    from .tweetchi.signals import tweetchi_beat, tweetchi_reply
    tweetchi_beat.connect(beat)
    tweetchi_reply.connect(reply)


def beat(tweetchi, updates=None):
    meta = updates and updates[-1] and updates[-1][1] or 1
    tweetchi.say('%s sheep' % meta, meta=meta + 1)


def reply(tweetchi, mentions=None):
    for m in mentions:
        tweetchi.update(
            '@%s Hello!' % m['user']['screen_name'],
            in_reply_to_status_id=m['id_str'])
