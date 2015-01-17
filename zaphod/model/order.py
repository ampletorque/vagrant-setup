from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Table, Column, ForeignKey, types, orm

from . import custom_types
from .base import Base
from .user_mixin import UserMixin


class Order(Base, UserMixin):
    __tablename__ = 'orders'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    cart_id = Column(None, ForeignKey('carts.id'), nullable=False, unique=True)
    user_id = Column(None, ForeignKey('users.id'), nullable=True)
    status = Column(types.String(255), nullable=False)

    user = orm.relationship('User', backref='orders', foreign_keys=user_id)

    @property
    def order_total(self):
        return self.cart.items_total + self.cart.shipping_total

    def ship_items(self, items):
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
    batch_id = Column(None, ForeignKey('pledge_batches.id'), nullable=True)

    status = Column(types.String(255), nullable=False)

    customer_comments = Column(types.UnicodeText, nullable=False, default=u'')

    cart = orm.relationship('Cart', backref='items')
    pledge_level = orm.relationship('PledgeLevel', backref='cart_items')
    batch = orm.relationship('PledgeBatch', backref='cart_items')


# XXX Maybe this should be a CartItem.shipment_id foreign key instead?
shipment_items = Table(
    'shipment_items',
    Base.metadata,
    Column('shipment_id', None, ForeignKey('shipments.id'), primary_key=True),
    Column('cart_item_id', None, ForeignKey('cart_items.id'),
           primary_key=True),
    mysql_engine='InnoDB')


class Shipment(Base, UserMixin):
    __tablename__ = 'shipments'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    order_id = Column(None, ForeignKey('orders.id'), nullable=False)
    tracking_number = Column(types.String(255), nullable=True)
    source = Column(types.CHAR(4), nullable=False)

    order = orm.relationship('Order', backref='shipments')
    items = orm.relationship('CartItem',
                             backref='shipments',
                             secondary=shipment_items)

    available_sources = {'hist': u'Historical Data Population',
                         'manl': u'Manually Marked as Shipped'}
