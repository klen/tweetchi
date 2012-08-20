from datetime import datetime

from ..core.models import BaseMixin
from ..ext import db


class Status(db.Model, BaseMixin):
    " Twitter status log. "

    __tablename__ = 'tweetchi_status'

    id_str = db.Column(db.String(20), nullable=False, unique=True)
    text = db.Column(db.String(200), nullable=False)
    in_reply_id_str = db.Column(db.String(20))
    screen_name = db.Column(db.String(30), nullable=False)
    self = db.Column(db.Boolean, default=False)

    @staticmethod
    def create_from_status(status, self=False):
        " Create myself from twitter status data. "

        return Status(
            id_str=status['id_str'],
            created_at=datetime.strptime(
                status['created_at'], "%a %b %d %H:%M:%S +0000 %Y"),
            text=status['text'],
            in_reply_id_str=status.get('in_reply_to_status_id_str'),
            screen_name=status['user']['screen_name'],
            self=self
        )

    def __eq__(self, other):
        return self.id_str == other.id_str

    def __ne__(self, other):
        return self.id_str != other.id_str

    def __lt__(self, other):
        return self.id_str < other.id_str

    def __le__(self, other):
        return self.id_str <= other.id_str

    def __gt__(self, other):
        return self.id_str > other.id_str

    def __ge__(self, other):
        return self.id_str >= other.id_str

    def __str__(self):
        return self.id_str

    def __repr__(self):
        return u"<Status '%s'>" % self.id_str
