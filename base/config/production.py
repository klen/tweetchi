" Production settings must be here. "

from .core import *
from os import path as op


SECRET_KEY = 'SecretKeyForSessionSigning'

# Mail (gmail config)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'username@gmail.com'
MAIL_PASSWORD = '*********'
DEFAULT_MAIL_SENDER = 'Admin < %s >' % MAIL_USERNAME

ADMINS = frozenset([MAIL_USERNAME])
COLLECT_STATIC_ROOT = op.join(op.dirname(ROOTDIR), 'static')

OAUTH_TWITTER = dict(
    base_url='http://api.twitter.com/1/',
    request_token_url='http://api.twitter.com/oauth/request_token',
    access_token_url='http://api.twitter.com/oauth/access_token',
    authorize_url='http://api.twitter.com/oauth/authorize',

    # flask-base-template app
    consumer_key='ydcXz2pWyePfc3MX3nxJw',
    consumer_secret='Pt1t2PjzKu8vsX5ixbFKu5gNEAekYrbpJrlsQMIwquc'
)

# Twitchi
# -------
TWEETCHI_CONSUMER_KEY = "MchK8XibR3cyEjm0U9Fwg"
TWEETCHI_CONSUMER_SECRET = "Z2NJuyf6lMU3lDTxoFAbKz7obkdOXjV3AgA4oLk1ns"
TWEETCHI_ACCOUNT = 'Tweetchi'
TWEETCHI_OAUTH_TOKEN = "633177233-o8Px6HR0uWWrun63xqCnO8iHSni2iFpMNoKgNQoJ"
TWEETCHI_OAUTH_SECRET = "AmSqA4bICxLP79CFW1wFvXXvygecoqhPDJbhuFYNQ2w"
BROKER_URL = 'redis://localhost:6379/0'

CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = 'localhost'

# pymode:lint_ignore=W0614,W404
# flake8: noqa
