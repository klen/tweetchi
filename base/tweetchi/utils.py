def get_new_followers(tweetchi, username):
    " Return difference between followers and friends. "

    followers = tweetchi.twitter_api.followers.ids(screen_name=username)
    followers = set(followers['ids'])

    friends = tweetchi.twitter_api.friends.ids(screen_name=username)
    friends = set(friends['ids'])

    return followers.difference(friends)


def as_tuple(obj):
    " Given obj return a tuple "

    if not obj:
        return tuple()

    if isinstance(obj, (tuple, set, list)):
        return tuple(obj)

    if hasattr(obj, '__iter__'):
        return obj

    return obj,
