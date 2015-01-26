from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm

from . import custom_types
from .address import make_address_columns
from .base import Base
from .user_mixin import UserMixin
from .comment import CommentMixin


class Order(Base, UserMixin, CommentMixin):
    __tablename__ = 'orders'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    cart_id = Column(None, ForeignKey('carts.id'), nullable=False, unique=True)
    user_id = Column(None, ForeignKey('users.id'), nullable=True)
    closed = Column(types.Boolean, nullable=False, default=False)
    shipping = make_address_columns('shipping')

    user = orm.relationship('User', backref='orders', foreign_keys=user_id)

    @property
    def order_total(self):
        """
        Return the total 'price' of this order, including shipping and all
        associated surcharges charged to the customer.
        """
        return self.cart.items_total + self.cart.shipping_total

    def update_status(self):
        """
        Update the .closed status of this order. It is 'closed' if and only if
        all of the cart items are closed and the order is fully paid.
        """
        raise NotImplementedError

    def ship_items(self, items, tracking_num, source, cost):
        """
        Add a new shipment to an order, marking the supplied items as shipped.
        """
        raise NotImplementedError


class Cart(Base):
    __tablename__ = 'carts'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)

    order = orm.relationship('Order', uselist=False, backref='cart')

    @property
    def items_total(self):
        return sum((ci.price_each * ci.qty_desired) for ci in self.cart.items)

    @property
    def shipping_total(self):
        return sum(ci.shipping_price for ci in self.cart.items)


class CartItem(Base):
    __tablename__ = 'cart_items'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    cart_id = Column(None, ForeignKey('carts.id'), nullable=False)
    pledge_level_id = Column(None, ForeignKey('pledge_levels.id'),
                             nullable=False)
    price_each = Column(custom_types.Money, nullable=False)
    qty_desired = Column(types.Integer, nullable=False, default=1)
    shipping_price = Column(custom_types.Money, nullable=False)
    crowdfunding = Column(types.Boolean, nullable=False)
    expected_delivery_date = Column(types.DateTime, nullable=True)
    shipped_date = Column(types.DateTime, nullable=True)
    shipment_id = Column(None, ForeignKey('shipments.id'), nullable=True)
    batch_id = Column(None, ForeignKey('pledge_batches.id'), nullable=True)

    status = Column(types.CHAR(8), nullable=False)

    customer_comments = Column(types.UnicodeText, nullable=False, default=u'')

    cart = orm.relationship('Cart', backref='items')
    pledge_level = orm.relationship('PledgeLevel', backref='cart_items')
    batch = orm.relationship('PledgeBatch', backref='cart_items')

    available_statuses = [
        ('init', 'Initial Value'),
        ('failed', 'Project Did Not Fund'),
        ('wait', 'Waiting for Production'),
        ('shipped', 'Shipped'),
        ('cancel', 'Cancelled'),
        # XXX Add more!
    ]

    @property
    def status_description(self):
        return self.available_statuses[self.status]

    def update_status(self):
        """
        Update the status of this item.
        """
        raise NotImplementedError

    def calculate_price(self):
        """
        Calculate the price of this item, including option values.
        """
        price = self.pledge_level.price
        for ov in self.option_values:
            price += ov.price_increase
        return price


class Shipment(Base, UserMixin):
    __tablename__ = 'shipments'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    order_id = Column(None, ForeignKey('orders.id'), nullable=False)
    tracking_number = Column(types.String(255), nullable=True)
    source = Column(types.CHAR(4), nullable=False)
    cost = Column(custom_types.Money, nullable=True)
    shipping = make_address_columns('shipping')

    order = orm.relationship('Order', backref='shipments')
    items = orm.relationship('CartItem', backref='shipments')

    available_sources = {'hist': u'Historical Data Population',
                         'manl': u'Manually Marked as Shipped'}

    @property
    def source_description(self):
        return self.available_sources[self.source]
