from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm

from . import custom_types, utils
from .base import Base, Session


class Acquisition(Base):
    """
    Represents a set of ``Item`` instances for a given SKU that were added to
    inventory concurrently.
    """
    __tablename__ = 'acquisitions'
    id = Column(types.Integer, primary_key=True)
    discriminator = Column(types.String(255), nullable=False)
    sku_id = Column(None, ForeignKey('skus.id'), nullable=False)
    acquisition_time = Column(types.DateTime, nullable=False,
                              default=utils.utcnow)

    sku = orm.relationship('SKU')
    items = orm.relationship('Item', backref='acquisition',
                             cascade="all, delete")

    __mapper_args__ = {
        'polymorphic_on': discriminator,
        'polymorphic_identity': 'Acquisition'
    }

    @property
    def qty(self):
        """
        The number of items currently being tracked for this acquisition.
        Excludes items which have been "destroyed" as a result of a negative
        inventory correction.
        """
        return Session.query(Item).filter_by(
            acquisition=self,
            destroy_time=None).count()

    def adjust_qty(self, qty):
        """
        Attempt to change the number of items in this specific
        acquisition. Returns a tuple (qty, actual_delta).

        The actual delta will be smaller than desired when trying to delete
        more Items than are in the acquisition.

        :param qty:
            The desired qty to adjust to.
        :type qty:
            int
        """
        current_qty = Session.query(Item).\
            filter_by(destroy_time=None, acquisition=self).\
            with_lockmode('update').\
            count()

        diff = qty - current_qty
        if diff == 0:
            return (current_qty, 0)

        elif diff > 0:
            for i in range(diff):
                si = Item(acquisition=self)
                Session.add(si)
            Session.flush()
            return (current_qty + diff, diff)

        elif diff < 0:
            item_ids = Session.query(Item.id).\
                filter_by(destroy_time=None,
                          acquisition=self,
                          cart_item_id=None).\
                limit(abs(diff)).with_lockmode('update').all()
            if item_ids:
                Item.query.filter(Item.id.in_(i for (i,) in item_ids)).\
                    update(values={
                        "destroy_time": utils.utcnow()
                    }, synchronize_session=False)
            Session.flush()
            delta = -len(item_ids)
            return (current_qty + delta, delta)


class VendorShipmentItem(Acquisition):
    """
    A line item on a received vendor shipment.
    """
    __tablename__ = 'vendor_shipment_items'
    acquisition_id = Column(None, ForeignKey('acquisitions.id'),
                            primary_key=True)
    vendor_shipment_id = Column(None, ForeignKey('vendor_shipments.id'),
                                nullable=False)
    vendor_order_item_id = Column(None, ForeignKey('vendor_order_items.id'),
                                  nullable=False)

    vendor_shipment = orm.relationship('VendorShipment', backref='items')
    vendor_order_item = orm.relationship('VendorOrderItem',
                                         backref='vendor_shipment_items')

    __mapper_args__ = {'polymorphic_identity': 'VendorShipmentItem'}


class InventoryAdjustment(Acquisition):
    """
    Manual changes to stock levels are represented by InventoryAdjustment
    records.
    """
    __tablename__ = 'inventory_adjustments'
    acquisition_id = Column(None, ForeignKey('acquisitions.id'),
                            primary_key=True)
    qty_diff = Column(types.Integer, nullable=False)
    user_id = Column(None, ForeignKey('users.id'), nullable=False)
    reason = Column(types.Unicode(255), nullable=False)

    user = orm.relationship('User')

    __mapper_args__ = {'polymorphic_identity': 'InventoryAdjustment'}


class Item(Base):
    """
    Represents one specific instance of stock. E.g. where "the red XL t-shirt"
    is one ``SKU``, "the red XL t-shirt serial numbered 1234" is one ``Item``.
    """
    __tablename__ = 'items'
    id = Column(types.Integer, primary_key=True)
    acquisition_id = Column(None, ForeignKey('acquisitions.id'),
                            nullable=False)
    create_time = Column(types.DateTime, nullable=False, default=utils.utcnow)
    cart_item_id = Column(None, ForeignKey('cart_items.id'), nullable=True)
    cost = Column(custom_types.Money, nullable=True)
    destroy_time = Column(types.DateTime, nullable=True)
    destroy_adjustment_id = Column(
        None,
        ForeignKey('inventory_adjustments.acquisition_id'),
        nullable=True)

    cart_item = orm.relationship('CartItem')
    destroy_adjustment = orm.relationship('InventoryAdjustment',
                                          foreign_keys=[destroy_adjustment_id])
