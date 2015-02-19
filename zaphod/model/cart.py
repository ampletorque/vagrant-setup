from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm

from . import custom_types
from .base import Base


class Cart(Base):
    __tablename__ = 'carts'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)

    order = orm.relationship('Order', uselist=False, backref='cart')

    @property
    def total(self):
        return sum(ci.total for ci in self.items)

    @property
    def items_total(self):
        return sum((ci.price_each * ci.qty_desired) for ci in self.items)

    @property
    def shipping_total(self):
        return sum(ci.shipping_price for ci in self.items)

    @property
    def non_physical(self):
        return all(ci.product.non_physical for ci in self.items)

    def refresh(self):
        """
        Refresh item statuses and reservations.
        """
        for item in self.items:
            item.refresh()


CROWDFUNDING = 0
PREORDER = 1
STOCK = 2


class CartItem(Base):
    __tablename__ = 'cart_items'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    cart_id = Column(None, ForeignKey('carts.id'), nullable=False)
    product_id = Column(None, ForeignKey('products.id'),
                        nullable=False)
    price_each = Column(custom_types.Money, nullable=False)
    qty_desired = Column(types.Integer, nullable=False, default=1)
    shipping_price = Column(custom_types.Money, nullable=False)
    stage = Column(types.Integer, nullable=False)

    expected_delivery_date = Column(types.DateTime, nullable=True)
    shipped_date = Column(types.DateTime, nullable=True)
    shipment_id = Column(None, ForeignKey('shipments.id'), nullable=True)
    batch_id = Column(None, ForeignKey('batches.id'), nullable=True)
    sku_id = Column(None, ForeignKey('skus.id'), nullable=False)

    status = Column(types.CHAR(16), nullable=False)

    cart = orm.relationship('Cart', backref='items')
    product = orm.relationship('Product', backref='cart_items')
    batch = orm.relationship('Batch', backref='cart_items')
    sku = orm.relationship('SKU', backref='cart_items')

    available_statuses = [
        ('cart', 'Pre-checkout'),
        ('unfunded', 'Project Not Yet Funded'),
        ('failed', 'Project Failed To Fund'),
        ('waiting', 'Waiting for Items'),
        ('payment pending', 'Payment Not Yet Processed'),
        ('payent failed', 'Payment Failed'),
        ('cancelled', 'Cancelled'),
        ('shipped', 'Shipped'),
        ('abandoned', 'Abandoned'),
        ('in process', 'In Process'),
        ('being packed', 'Being Packed'),
    ]

    @property
    def status_description(self):
        return self.available_statuses[self.status]

    def update_status(self, new_value):
        """
        Update the status of this item.
        """
        raise NotImplementedError

    def calculate_price(self):
        """
        Calculate the price of this item, including option values.
        """
        price = self.product.price
        # XXX
        # for ov in self.option_values:
        #     price += ov.price_increase
        return price

    @property
    def total(self):
        return (self.price_each + self.shipping_price) * self.qty_desired

    @property
    def qty_reserved(self):
        # XXX
        return 0

    def refresh(self):
        """
        Refresh status and reservations.
        """
        # XXX Implement this!
        pass
