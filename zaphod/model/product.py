from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from decimal import Decimal

from sqlalchemy import Column, ForeignKey, types, orm
from sqlalchemy.sql import func, not_

from . import custom_types
from .base import Base, Session
from .image import ImageMixin
from .cart import Cart, CartItem


class Batch(Base):
    """
    A planned production batch for a product.
    """
    __tablename__ = 'batches'
    id = Column(types.Integer, primary_key=True)
    product_id = Column(None, ForeignKey('products.id'), nullable=False)
    # None for qty means infinite units can be delivered in this batch.
    qty = Column(types.Integer, nullable=True)
    ship_date = Column(types.DateTime, nullable=False)


class Product(Base, ImageMixin):
    """
    A product associated with a product. This can be thought of as comparable
    to a 'pledge level', but is also used for projects which aren't and weren't
    crowdfunding campaigns.
    """
    __tablename__ = 'products'
    id = Column(types.Integer, primary_key=True)
    project_id = Column(None, ForeignKey('projects.node_id'), nullable=False)
    name = Column(types.Unicode(255), nullable=False, default=u'')
    international_available = Column(types.Boolean, nullable=False,
                                     default=False)
    international_surcharge = Column(custom_types.Money, nullable=False,
                                     default=0)
    gravity = Column(types.Integer, nullable=False, default=0)
    non_physical = Column(types.Boolean, nullable=False, default=False)
    published = Column(types.Boolean, nullable=False, default=False)
    price = Column(custom_types.Money, nullable=False, default=0)
    accepts_preorders = Column(types.Boolean, nullable=False, default=False)
    in_stock = Column(types.Boolean, nullable=False, default=False)
    fulfillment_fee = Column(custom_types.Money, nullable=False,
                             default=Decimal('2.50'))

    hs_code = Column(types.String(255), nullable=False, default=u'')
    # In kg
    shipping_weight = Column(types.Float, nullable=False, default=0)
    # In cm
    box_length = Column(types.Float, nullable=False, default=0)
    box_width = Column(types.Float, nullable=False, default=0)
    box_height = Column(types.Float, nullable=False, default=0)

    batches = orm.relationship('Batch', backref='product')

    def select_batch(self, qty):
        """
        Return the batch that a new order of qty ``qty`` should be allocated
        to.
        """
        consumed = self.qty_claimed
        for batch in self.batches:
            if (not batch.qty) or ((consumed + qty) < batch.qty):
                return batch
            consumed -= batch.qty

    @property
    def current_batch(self):
        """
        Return the currently 'open' batch for this product.
        """
        return self.select_batch(qty=1)

    @property
    def current_ship_date(self):
        """
        Return the delivery date for the currently 'open' batch.
        """
        return self.current_batch.ship_date

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
            filter(not_(CartItem.status.in_(['canc', 'frau']))).\
            scalar() or 0

    @property
    def published_options(self):
        # XXX Turn into a relationship
        return [opt for opt in self.options if opt.published]

    @property
    def is_available(self):
        return self.non_physical or self.in_stock or bool(self.current_batch)

    def calculate_in_stock(self):
        return any(sku.qty_available > 0 for sku in self.skus)

    def update_in_stock(self):
        self.in_stock = self.calculate_in_stock()


class Option(Base):
    """
    A product option which allows for per-item configuration.
    """
    __tablename__ = 'options'
    id = Column(types.Integer, primary_key=True)
    product_id = Column(None, ForeignKey('products.id'), nullable=False)
    name = Column(types.Unicode(255), nullable=False, default=u'')
    gravity = Column(types.Integer, nullable=False, default=0)
    published = Column(types.Boolean, nullable=False, default=False)

    product = orm.relationship('Product', backref='options')

    @property
    def published_values(self):
        # XXX Turn into a relationship
        return [val for val in self.values if val.published]


class OptionValue(Base):
    """
    A single possible 'choice' for an option.
    """
    __tablename__ = 'option_values'
    id = Column(types.Integer, primary_key=True)
    option_id = Column(None, ForeignKey('options.id'), nullable=False)
    description = Column(types.Unicode(255), nullable=False, default=u'')
    price_increase = Column(custom_types.Money, nullable=False, default=0)
    gravity = Column(types.Integer, nullable=False, default=0)
    is_default = Column(types.Boolean, nullable=True)
    published = Column(types.Boolean, nullable=False, default=False)

    option = orm.relationship('Option', backref='values')
