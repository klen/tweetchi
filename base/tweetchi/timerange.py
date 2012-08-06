from datetime import time, datetime


class timerange():

    def __init__(self, frm, to):
        self.frm = self._to_time(frm)
        self.to = self._to_time(to)
        self.op = lambda x, y: x and y
        if self.frm > self.to:
            self.op = lambda x, y: x or y

    @staticmethod
    def _to_time(value):

        if isinstance(value, time):
            return value

        elif isinstance(value, datetime):
            return value.time()

        elif isinstance(value, (list, tuple)):
            return time(*value)

        elif isinstance(value, basestring):
            return time(*map(int, value.replace('.', ':').strip().split(':')))

        raise ValueError('Value must be is instance time or datetime. ')

    def __contains__(self, value):
        value = self._to_time(value)
        return self.op(value <= self.to, value >= self.frm)

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return self.frm == value.frm and self.to == value.to
        raise ValueError('Value must be instance of timerange')

    def __repr__(self):
        return "timerange(%s, %s)" % (self.frm.strftime('%H:%M'), self.to.strftime('%H:%M'))
