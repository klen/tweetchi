def register_app(app):
    " Configure application. "

    from .tweetchi import tweetchi
    tweetchi.init_app(app)
