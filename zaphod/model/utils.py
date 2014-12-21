from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime

__all__ = ['utcnow']


def utcnow():
    """
    Wraps the ``datetime.utcnow()`` function for use inside the model. Provides
    a convenient access point for mocking all ``utcnow()`` calls.
    """
    return datetime.datetime.utcnow()
