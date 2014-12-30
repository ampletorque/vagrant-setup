from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from sqlalchemy import Column, ForeignKey, types, orm

from . import utils
from .base import Base, Session
from .node import Node
from .image import ImageMixin


class PledgeBatch(Base):
    __tablename__ = 'pledge_batches'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    pledge_level_id = Column(None, ForeignKey('pledge_levels.id'),
                             nullable=False)
    # None for qty means infinite units can be delivered in this batch.
    qty = Column(types.Integer, nullable=True)
    delivery_date = Column(types.DateTime, nullable=False)


class PledgeLevel(Base, ImageMixin):
    __tablename__ = 'pledge_levels'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    project_id = Column(None, ForeignKey('projects.node_id'), nullable=False)
    name = Column(types.Unicode(255), nullable=False, default=u'')
    gravity = Column(types.Integer, nullable=False, default=0)
    non_physical = Column(types.Boolean, nullable=False, default=False)

    batches = orm.relationship('PledgeBatch', backref='pledge_level')

    @property
    def current_batch(self):
        """
        Return the batch that new orders for this pledge level should be
        allocated to.
        """
        consumed = self.qty_claimed
        for batch in self.batches:
            if (not batch.qty) or (consumed < batch.qty):
                return batch
            consumed -= batch.qty

    @property
    def current_delivery_date(self):
        return self.current_batch.delivery_date

    @property
    def qty_available(self):
        # XXX Performance
        qty = 0
        for batch in self.batches:
            if not batch.qty:
                return
            else:
                qty += batch.qty
        return qty

    @property
    def qty_remaining(self):
        # XXX Performance
        if self.qty_available:
            return max(self.qty_available - self.qty_claimed, 0)

    @property
    def qty_claimed(self):
        # XXX Performance
        return Session.query(func.sum(CartItem.qty_desired)).\
            join(CartItem.cart).\
            join(Cart.order).\
            filter(CartItem.product == self).\
            filter(not_(Order.status.in_(['canc', 'frau']))).\
            scalar() or 0
