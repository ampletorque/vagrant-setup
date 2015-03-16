from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import event

from .address import *
from .article import *
from .base import *
from .cart import *
from .creator import *
from .lead import *
from .image import *
from .item import *
from .node import *
from .order import *
from .payment import *
from .product import *
from .project import *
from .provider import *
from .sku import *
from .tag import *
from .user import *
from .user_mixin import *
from .utils import *
from .vendor import *


class WriteBlocked(Exception):
    """
    Raised when a write is attempted to the model while the model is
    initialized in read-only mode.
    """
    pass


def init_model(engine, read_only=False):
    """
    Provide a SQLAlchemy engine for the database model to perform operations
    against. Call this before using any of the tables or classes in this model.

    After the model has been initialized, the ``Session`` object provides a
    scoped session for ORM access.

    :param engine:
        A SQLAlchemy engine to use.

    :param read_only:
        Specify whether or not the session should allow changes to be flushed
        to the DB. If this is True, an event listener will be installed which
        blocks any data from being flushed, raising a ``WriteBlocked``
        exception.

    :type read_only:
        bool
    """
    Session.configure(bind=engine)
    Base.metadata.bind = engine

    if read_only:
        def check_dirty(session, flush_context, instance):
            """
            If the session is modified, raise an exception. Used by an event
            listener to effectively make the session read-only; this exception
            can be cuaght by higher level controller flow code to serve up a
            'maintenance' response code.
            """
            raise WriteBlocked("attempted change to DB, but session is "
                               "currently read-only")

        event.listen(Session, 'before_flush', check_dirty)
