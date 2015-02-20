from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm

from pyramid_es.mixin import ElasticMixin, ESMapping, ESField

from . import custom_types
from .address import make_address_columns
from .base import Base
from .user_mixin import UserMixin
from .comment import CommentMixin


class Order(Base, UserMixin, CommentMixin, ElasticMixin):
    __tablename__ = 'orders'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    cart_id = Column(None, ForeignKey('carts.id'), nullable=False, unique=True)
    user_id = Column(None, ForeignKey('users.id'), nullable=True)
    closed = Column(types.Boolean, nullable=False, default=False)
    shipping = make_address_columns('shipping')

    customer_comments = Column(types.UnicodeText, nullable=False, default=u'')

    user = orm.relationship('User', backref='orders', foreign_keys=user_id)

    @property
    def total(self):
        """
        Return the total 'price' of this order, including shipping and all
        associated surcharges charged to the customer.
        """
        return self.cart.items_total + self.cart.shipping_total

    @property
    def unauthorized_amount(self):
        # FIXME XXX
        return 0

    @property
    def any_billing(self):
        return None
        for payment in self.payments:
            if hasattr(payment, 'method'):
                return payment.method.billing

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

    @classmethod
    def elastic_mapping(cls):
        return ESMapping(
            analyzer='content',
            properties=ESMapping(
                ESField('id'),
                ESField('user',
                        filter=lambda user: {
                            'name': user.name,
                            'email': user.email
                        } if user else {}),
                ESField('shipping', filter=lambda addr: {
                    'full_name': addr.full_name,
                    'address1': addr.address1,
                    'address2': addr.address2,
                    'phone': addr.phone,
                    'company': addr.company,
                    'city': addr.city,
                    'postal_code': addr.postal_code,
                    'country_name': addr.country_name,
                }),
            ))


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
