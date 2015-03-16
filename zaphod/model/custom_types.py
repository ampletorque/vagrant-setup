from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json

from sqlalchemy import types

__all__ = ['Money']


class Money(types.TypeDecorator):
    """
    A wrapper on a Numeric datatype specified to be appropriate for money.
    """
    impl = types.Numeric

    def __init__(self, *args, **kwargs):
        if 'precision' in kwargs:
            raise TypeError("'precision' cannot be used with this type.")
        if 'scale' in kwargs:
            raise TypeError("'scale' cannot be used this type.")
        types.TypeDecorator.__init__(self, precision=10,
                                     scale=2, *args, **kwargs)


class JSON(types.TypeDecorator):
    """
    Store JSON-serialized objects. Note that these objects are not "mutable" in
    that the sqlalchemy session will not detect and persist changes to a
    persisted object (e.g. for dicts or lists). To store changes to these
    objects, create a whole new object by way of .copy().
    """
    impl = types.String

    def process_bind_param(self, value, dialect):
        # Convert from object to serialized JSON for DB storage.
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        # Convert from serialized JSON from DB to object.
        return json.loads(value)
