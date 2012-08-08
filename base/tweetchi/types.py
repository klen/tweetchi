#!/usr/bin/env python
# coding: utf-8

from datetime import datetime


class Status:

    def __init__(self, data):
        self.id = data['id_str']
        self.created_at = datetime.strptime(data['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
        self.text = data['text']
        self.reply_id = data.get('in_reply_to_status_id_str')
        self.user = User(data['user'])
        self.data = data

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __str__(self):
        return self.id

    def __repr__(self):
        return u"<Status '%s'>" % self.id

    def __getitem__(self, key):
        return self.data[key]


class User:

    def __init__(self, data):
        self.screen_name = data['screen_name']
        self.id = str(data['id_str'])
        self.data = data

    def __str__(self):
        return self.screen_name

    def __repr__(self):
        return "<User '%s'>" % str(self)

    def __getitem__(self, key):
        return self.data[key]
