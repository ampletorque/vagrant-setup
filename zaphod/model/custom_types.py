from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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
