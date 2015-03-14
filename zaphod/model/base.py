from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension


__all__ = ['Base', 'Session']


"""
SQLAlchemy session used for the entire Zaphod app. The Zope transaction
extension is used, so this session automatically commits transactions in the
scope of a request. Transactions should not be manually committed.
"""
Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class _Base(object):

    @classmethod
    def get(cls, id):
        """
        Get an instance of this class by primary key.

        :param id:
            Primary key value.
        :return:
            Instance of the class.
        """
        return Session.query(cls).get(id)


Base = declarative_base(cls=_Base)
