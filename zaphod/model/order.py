from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm

from pyramid_es.mixin import ElasticMixin, ESMapping, ESField

from . import utils, custom_types
from .address import make_address_columns
from .base import Base
from .user_mixin import UserMixin
from .comment import CommentMixin


class Order(Base, UserMixin, CommentMixin, ElasticMixin):
    """
    A customer order that has been placed.
    """
    __tablename__ = 'orders'
    id = Column(types.Integer, primary_key=True)
    cart_id = Column(None, ForeignKey('carts.id'), nullable=False, unique=True)
    user_id = Column(None, ForeignKey('users.id'), nullable=False)
    closed = Column(types.Boolean, nullable=False, default=False)
    shipping = make_address_columns('shipping')

    customer_comments = Column(types.UnicodeText, nullable=False, default=u'')

    user = orm.relationship('User', backref='orders', foreign_keys=user_id)

    @property
    def total_amount(self):
        """
        Return the total 'price' of this order, including shipping and all
        associated surcharges charged to the customer.
        """
        return self.cart.items_total + self.cart.shipping_total

    @property
    def shipping_amount(self):
        return self.cart.shipping_total

    @property
    def paid_amount(self):
        "The amount currently paid, *not* including authorizes."
        return sum(p.amount for p in self.payments if p.valid)

    @property
    def unpaid_amount(self):
        "The amount currently unpaid. Authorizes don't count as paid."
        return self.total_amount - self.paid_amount

    @property
    def authorized_amount(self):
        "The amount that could be paid if we captured all payments."
        tot = 0
        for p in (pp for pp in self.payments if pp.valid):
            if (hasattr(p, 'authorized_amount') and
                    (not p.captured_time)):
                # An uncaptured, unvoided credit card payment.
                tot += p.authorized_amount
            else:
                tot += p.amount
        return tot

    @property
    def unauthorized_amount(self):
        "The amount we need to get from the customer."
        return max(0, self.total_amount - self.authorized_amount)

    @property
    def any_billing(self):
        """
        Retrun any billing address that is associated with this order, or None
        if no billing addresses are associated.
        """
        for payment in self.payments:
            if hasattr(payment, 'method'):
                return payment.method.billing

    def update_status(self):
        """
        Update the .closed status of this order. It is 'closed' if and only if
        all of the cart items are closed and the order is fully paid.
        """
        self.closed = all(ci.closed for ci in self.cart.items)

    def cancel(self, items, reason, user):
        """
        Cancel items on this order.
        """
        for item in items:
            item.release_stock()
            item.update_status('cancelled')
        comment_body = 'Order cancelled.'
        if reason:
            comment_body += (' Details: %s' % reason)
        else:
            comment_body += ' No details specified.'
        self.add_comment(user, comment_body)
        self.update_status()

    def ship_items(self, items, tracking_number, cost, shipped_by_creator,
                   user):
        """
        Add a new shipment to an order, marking the supplied items as shipped.
        """
        utcnow = utils.utcnow()
        shipment = Shipment(
            tracking_number=tracking_number,
            cost=cost,
            shipped_by_creator=shipped_by_creator,
            created_by=user,
            shipping=self.shipping,
        )
        self.shipments.append(shipment)
        for item in items:
            item.shipped_time = utcnow
            item.shipment = shipment
            item.update_status('shipped')
        self.update_status()

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
    """
    A shipment that has been shipped against this order.
    """
    __tablename__ = 'shipments'
    id = Column(types.Integer, primary_key=True)
    order_id = Column(None, ForeignKey('orders.id'), nullable=False)
    tracking_number = Column(types.String(255), nullable=True)
    cost = Column(custom_types.Money, nullable=True)
    shipped_by_creator = Column(types.Boolean, nullable=False)
    shipping = make_address_columns('shipping')
    tracking_email_sent = Column(types.Boolean, nullable=False, default=False)

    order = orm.relationship('Order', backref='shipments')
    items = orm.relationship('CartItem', backref='shipments')
