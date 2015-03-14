from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six

from sqlalchemy import Column, ForeignKey, types, orm
from sqlalchemy.ext.declarative import declared_attr

from . import utils
from .base import Base


class CommentMixin(object):
    """
    Mixin class which provides admin comment tracking on a model object.
    """
    @declared_attr
    def comments(cls):
        if not issubclass(cls, Base):
            return

        table_name = cls.__tablename__
        if six.PY3:
            type_name = cls.__name__ + 'Comment'
        else:
            type_name = cls.__name__ + b'Comment'

        cls.Comment = type(
            type_name,
            (Base,),
            dict(__tablename__='%s_comments' % table_name,
                 id=Column('id', types.Integer, primary_key=True),
                 source_id=Column('source_id', None,
                                  ForeignKey('%s.id' % table_name),
                                  nullable=False),
                 created_time=Column('created_time', types.DateTime,
                                     nullable=False, default=utils.utcnow),
                 created_by_id=Column('created_by_id', None,
                                      ForeignKey('users.id'), nullable=False),
                 body=Column('body', types.UnicodeText, nullable=False),
                 created_by=orm.relationship(
                     'User',
                     foreign_keys='%s.created_by_id' % type_name)))

        return orm.relationship(cls.Comment,
                                foreign_keys=[cls.Comment.source_id],
                                order_by=cls.Comment.id)

    @property
    def new_comment(self):
        return u''

    @new_comment.setter
    def new_comment(self, value):
        if value:
            user, body = value
            self.add_comment(body, user)

    def add_comment(self, user, body):
        """
        Add a new comment to this object.
        """
        self.comments.append(self.Comment(
            created_by=user,
            body=body,
        ))
