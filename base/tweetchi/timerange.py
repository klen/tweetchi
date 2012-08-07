from datetime import time, datetime, date
from pytz import utc, timezone


class timerange:

    def __init__(self, *rang, **kwargs):

        if len(rang) == 1:
            rang = rang[0][0], rang[0][1]

        self.tz = kwargs.pop('tz', utc)
        if isinstance(self.tz, basestring):
            self.tz = timezone(self.tz)

        self.frm, self.to = map(self._to_time, rang)
        self.op = lambda x, y: x and y
        if self.frm > self.to:
            self.op = lambda x, y: x or y

    def _to_time(self, value):

        if isinstance(value, time):
            return self._to_tz(value)

        elif isinstance(value, datetime):
            return self._to_tz(value.timetz())

        elif isinstance(value, (list, tuple)):
            return self._to_tz(time(*value))

        elif isinstance(value, basestring):
            return self._to_tz(time(*map(int, value.replace('.', ':').strip().split(':'))))

        raise ValueError('Value must be is instance time or datetime. ')

    def _to_tz(self, value):
        if not value.tzinfo:
            value = value.replace(tzinfo=self.tz)
        temp = datetime.combine(date.today(), value) - value.tzinfo._utcoffset
        return temp.time()

    def __contains__(self, value):
        value = self._to_time(value)
        return self.op(value <= self.to, value >= self.frm)

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return self.frm == value.frm and self.to == value.to
        raise ValueError('Value must be instance of timerange')

    def __getitem__(self, value):
        value = bool(value)
        return self.to if value else self.frm

    def __repr__(self):
        return "timerange(%s, %s)" % (self.frm.strftime('%H:%M'), self.to.strftime('%H:%M'))
