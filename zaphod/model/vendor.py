from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm
from sqlalchemy.sql import func

from . import custom_types
from .address import make_address_columns
from .base import Base, Session
from .user_mixin import UserMixin
from .comment import CommentMixin
from .item import VendorShipmentItem, Item


class Vendor(Base, UserMixin, CommentMixin):
    """
    A vendor from which wholesale inventory is purchased.
    """
    __tablename__ = 'vendors'
    id = Column(types.Integer, primary_key=True)
    name = Column(types.Unicode(50), nullable=False)
    active = Column(types.Boolean, nullable=False, default=True)
    mailing = make_address_columns('mailing')


class VendorOrder(Base, UserMixin, CommentMixin):
    """
    An order placed from an upstream vendor.
    """
    __tablename__ = 'vendor_orders'
    id = Column(types.Integer, primary_key=True)
    vendor_id = Column(None, ForeignKey('vendors.id'), nullable=False)
    reference = Column(types.Unicode(255), nullable=False, default=u'')
    description = Column(types.UnicodeText, nullable=False, default=u'')

    placed_by_id = Column(None, ForeignKey('users.id'), nullable=True)
    placed_time = Column(types.DateTime, nullable=True)

    status = Column(types.String(255), nullable=False)

    vendor = orm.relationship('Vendor', backref='orders')
    placed_by = orm.relationship('User', foreign_keys=[placed_by_id])

    available_statuses = {
        'crea': u'Order Created',
        'sent': u'Order Sent',
        'conf': u'Order Confirmed',
        'part': u'Order Partially Received',
        'recd': u'Order Received',
        'void': u'Order Void',
    }

    @property
    def status_description(self):
        return self.available_statuses[self.status]


class VendorOrderItem(Base):
    """
    A line item in a vendor order.
    """
    __tablename__ = 'vendor_order_items'
    id = Column(types.Integer, primary_key=True)
    vendor_order_id = Column(None, ForeignKey('vendor_orders.id'),
                             nullable=False)

    qty_ordered = Column(types.Integer, nullable=False, default=0)
    cost = Column(custom_types.Money, nullable=True)

    sku_id = Column(None, ForeignKey('skus.id'), nullable=False)

    order = orm.relationship('VendorOrder', backref='items')
    sku = orm.relationship('SKU')

    @property
    def qty_received(self):
        return Session.query(Item).\
            join(Item.acquisition.of_type(VendorShipmentItem)).\
            filter(VendorShipmentItem.vendor_order_item == self).\
            count()

    @property
    def qty_invoiced(self):
        return Session.query(func.sum(VendorInvoiceItem.qty_invoiced)).\
            filter(VendorInvoiceItem.vendor_order_item == self).\
            scalar() or 0


class VendorInvoice(Base, UserMixin, CommentMixin):
    """
    An invoice indicating costs due for a vendor order. Invoices should be used
    to track all costs paid to a vendor: that is, no payments should ever be
    made that do not match an invoice.
    """
    __tablename__ = 'vendor_invoices'
    id = Column(types.Integer, primary_key=True)
    vendor_order_id = Column(None, ForeignKey('vendor_orders.id'),
                             nullable=False)

    invoice_num = Column(types.Unicode(75), nullable=False, default=u'',
                         doc="Vendor provided invoice identifier.")
    invoice_date = Column(types.Date, nullable=True)

    shipping_date = Column(types.Date, nullable=True)
    shipping_cost = Column(custom_types.Money, nullable=False, default=0)

    tax = Column(custom_types.Money, nullable=False, default=0)
    drop_ship_fee = Column(custom_types.Money, nullable=False, default=0)

    discount = Column(custom_types.Money, nullable=False, default=0,
                      doc=('A discount (e.g. early pay discount) associated '
                           'with this invoice. If ``discount_applies`` is '
                           'True, this will be subtracted from item costs '
                           '(weighted like other invoice fees). Even if a '
                           'discount isn\'t applied, it can still be noted '
                           'for future documentation.'))
    discount_applies = Column(types.Boolean, nullable=False, default=False,
                              doc=('Indicates whether or not the discount '
                                   'was applied to this invoice.'))

    # For wire transfer fees, escrow fees, etc.
    bank_fee = Column(custom_types.Money, nullable=False, default=0)

    vendor_order = orm.relationship('VendorOrder', backref='invoices')


class VendorInvoiceItem(Base):
    """
    A line item on a vendor invoice.
    """
    __tablename__ = 'vendor_invoice_items'
    id = Column(types.Integer, primary_key=True)
    vendor_invoice_id = Column(None, ForeignKey('vendor_invoices.id'),
                               nullable=False)
    vendor_order_item_id = Column(None, ForeignKey('vendor_order_items.id'),
                                  nullable=False)

    vendor_invoice = orm.relationship('VendorInvoice', backref='items')
    vendor_order_item = orm.relationship('VendorOrderItem',
                                         backref='vendor_invoice_items')

    qty_invoiced = Column(types.Integer, nullable=False)
    cost_each = Column(custom_types.Money, nullable=False)


class VendorShipment(Base, UserMixin):
    """
    A shipment of stock received against a vendor order.
    """
    __tablename__ = 'vendor_shipments'
    id = Column(types.Integer, primary_key=True)
    vendor_order_id = Column(None, ForeignKey('vendor_orders.id'),
                             nullable=False)
    description = Column(types.UnicodeText, nullable=False, default=u'')

    vendor_order = orm.relationship('VendorOrder', backref='shipments')
