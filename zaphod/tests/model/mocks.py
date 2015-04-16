import datetime

from mock import patch


def patch_utcnow(*args, **kwargs):

    class FakeDateTime(datetime.datetime):
        @classmethod
        def utcnow(cls):
            return cls(*args, **kwargs)

    return patch('datetime.datetime', FakeDateTime)
