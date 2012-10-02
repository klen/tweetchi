" Production settings must be here. "

from .core import *
from os import path as op


MODE = 'production'
SECRET_KEY = 'SecretKeyForSessionSigning'
ADMINS = MAIL_USERNAME and [MAIL_USERNAME] or None

# flask.ext.collect
# -----------------
COLLECT_STATIC_ROOT = op.join(op.dirname(ROOTDIR), 'static')

# auth.oauth
# ----------
OAUTH_TWITTER = dict(
    consumer_key='750sRyKzvdGPJjPd96yfgw',
    consumer_secret='UGcyjDCUOb1q44w1nUk8FA7aXxvwwj1BCbiFvYYI',
)

OAUTH_FACEBOOK = dict(
    consumer_key='413457268707622',
    consumer_secret='48e9be9f4e8abccd3fb916a3f646dd3f',
)

OAUTH_GITHUB = dict(
    consumer_key='8bdb217c5df1c20fe632',
    consumer_secret='a3aa972b2e66e3fac488b4544d55eda2aa2768b6',
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

# dealer
DEALER_PARAMS = dict(
    backends=('git', 'mercurial', 'simple', 'null')
)

# pymode:lint_ignore=W0614,W404
