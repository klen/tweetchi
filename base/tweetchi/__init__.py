" Flask based twitter bot application. "


def loader_meta(app):
    " Configure application. "

    from .tweetchi import tweetchi
    tweetchi.init_app(app)
