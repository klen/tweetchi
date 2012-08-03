from blinker import Namespace


_signals = Namespace()

tweetchi_beat = _signals.signal('tweetchi-beat')
tweetchi_reply = _signals.signal('tweetchi-reply')
