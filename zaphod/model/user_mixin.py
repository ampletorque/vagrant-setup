from sqlalchemy import Column, ForeignKey, types, orm
from sqlalchemy.ext.declarative import declared_attr

from . import utils

__all__ = ['UserMixin']


class UserMixin(object):
    """
    Use as a mixin on a sqlalchemy declarative class to add the created_by,
    created_time, updated_by, and updated_time attributes to track modification
    history.
    """
    @declared_attr
    def created_by_id(cls):
        return Column(None, ForeignKey('users.id'), nullable=False, default=1)

    @declared_attr
    def created_time(cls):
        return Column('created_time', types.DateTime,
                      default=utils.utcnow, nullable=False)

    @declared_attr
    def updated_by_id(cls):
        return Column(None, ForeignKey('users.id'), nullable=False, default=1)

    @declared_attr
    def updated_time(cls):
        return Column('updated_time', types.DateTime,
                      default=utils.utcnow, nullable=False)

    @declared_attr
    def created_by(cls):
        return orm.relationship(
            'User',
            foreign_keys='%s.created_by_id' % cls.__name__,
            remote_side='User.id')

    @declared_attr
    def updated_by(cls):
        return orm.relationship(
            'User',
            foreign_keys='%s.updated_by_id' % cls.__name__,
            remote_side='User.id')
