from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension


__all__ = ['Base', 'Session']


Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
