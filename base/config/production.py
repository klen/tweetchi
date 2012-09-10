" Production settings must be here. "

from .core import *
from os import path as op


SECRET_KEY = 'SecretKeyForSessionSigning'
ADMINS = frozenset([MAIL_USERNAME])

# flask.ext.collect
# -----------------
COLLECT_STATIC_ROOT = op.join(op.dirname(ROOTDIR), 'static')

# auth.oauth
# ----------
OAUTH_TWITTER = dict(
    # flask-base-template app
    consumer_key='ydcXz2pWyePfc3MX3nxJw',
    consumer_secret='Pt1t2PjzKu8vsX5ixbFKu5gNEAekYrbpJrlsQMIwquc'
)

# Cache
CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = 'localhost'

# Twitchi
# -------
TWEETCHI_CONSUMER_KEY = "MchK8XibR3cyEjm0U9Fwg"
TWEETCHI_CONSUMER_SECRET = "Z2NJuyf6lMU3lDTxoFAbKz7obkdOXjV3AgA4oLk1ns"
TWEETCHI_ACCOUNT = 'Tweetchi'
TWEETCHI_OAUTH_TOKEN = "633177233-o8Px6HR0uWWrun63xqCnO8iHSni2iFpMNoKgNQoJ"
TWEETCHI_OAUTH_SECRET = "AmSqA4bICxLP79CFW1wFvXXvygecoqhPDJbhuFYNQ2w"
BROKER_URL = 'redis://localhost:6379/0'

# pymode:lint_ignore=W0614,W404
