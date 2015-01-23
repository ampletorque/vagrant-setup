from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm

from .base import Base
from .user_mixin import UserMixin
from .comment import CommentMixin


class VendorOrder(Base, UserMixin, CommentMixin):
    __tablename__ = 'vendor_orders'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    creator_id = Column(None, ForeignKey('creators.node_id'), nullable=False)
    status = Column(types.String(255), nullable=False)

    creator = orm.relationship('Creator', backref='orders')


class VendorOrderItem(Base):
    __tablename__ = 'vendor_order_items'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    vendor_order_id = Column(None, ForeignKey('vendor_orders.id'),
                             nullable=False)
    pledge_level_id = Column(None, ForeignKey('pledge_levels.id'),
                             nullable=False)

    order = orm.relationship('VendorOrder', backref='items')
    pledge_level = orm.relationship('PledgeLevel')
