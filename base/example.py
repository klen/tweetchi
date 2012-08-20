def register_app(app):
    " Configure application. "

    from .tweetchi.signals import tweetchi_beat, tweetchi_reply
    from datetime import timedelta

    tweetchi_beat.connect(beat)
    tweetchi_reply.connect(reply)

    app.config['TWEETCHI_BEAT_SCHEDULE'] = timedelta(seconds=15)

register_app.priority = 10


def beat(tweetchi, updates=None):
    meta = updates and updates[-1] and updates[-1][1] or 1
    meta += 1
    tweetchi.say('%s sheep' % meta, meta=meta)


def reply(tweetchi, mentions):
    for mention in mentions:
        tweetchi.update(
            '@%s Hello!' % (mention.screen_name),
            in_reply_to_status_id=mention.id_str)
