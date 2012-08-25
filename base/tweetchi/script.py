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


@manager.command
def tweetchi_new_followers(username):
    from .tweetchi import tweetchi
    from .utils import get_new_followers

    print get_new_followers(tweetchi, username)
