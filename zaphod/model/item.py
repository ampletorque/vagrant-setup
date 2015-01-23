from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Table, Column, ForeignKey, types, orm

from . import custom_types, utils
from .base import Base


# XXX Should we have a separate concept for 'Acquisition' or something
# similar?


class Item(Base):
    __tablename__ = 'items'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    sku_id = Column(None, ForeignKey('skus.id'), nullable=False)
    create_time = Column(types.DateTime, nullable=False, default=utils.utcnow)
    destroy_time = Column(types.DateTime, nullable=False)
    cart_item_id = Column(None, ForeignKey('cart_items.id'), nullable=True)
    cost = Column(custom_types.Money, nullable=True)
