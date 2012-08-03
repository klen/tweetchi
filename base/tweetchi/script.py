from ..ext import manager


@manager.command
def tweetchi_dance():
    " Get twitter OAuth tokens. "
    from .tweetchi import tweetchi
    tweetchi.dance()


@manager.command
def tweetchi_update(message):
    " Post to twitter. "
    from .tweetchi import tweetchi
    tweetchi.update(message)
