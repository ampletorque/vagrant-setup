from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Table, Column, ForeignKey, types, orm
from sqlalchemy.sql import or_
from sqlalchemy.orm.exc import NoResultFound

from . import utils
from .base import Base, Session
from .product import OptionValue
from .item import Acquisition, Item, InventoryAdjustment
from .cart import CartItem


sku_option_values = Table(
    'sku_option_values',
    Base.metadata,
    Column('sku_id', None, ForeignKey('skus.id'), primary_key=True),
    Column('option_value_id', None, ForeignKey('option_values.id'),
           primary_key=True),
    mysql_engine='InnoDB')


class SKU(Base):
    """
    A stock-keeping-unit, representing a specific variant of a product. Any
    stock items of the same "SKU" can be interchanged with each other without
    any distinction.
    """
    __tablename__ = 'skus'
    id = Column(types.Integer, primary_key=True)
    product_id = Column(None, ForeignKey('products.id'), nullable=False)

    product = orm.relationship('Product', backref='skus')

    option_values = orm.relationship('OptionValue',
                                     collection_class=set,
                                     secondary=sku_option_values)

    @property
    def qty(self):
        """
        Total quantity of unshipped stock, including stock associated with
        unshipped orders.
        """
        return Session.query(Item).\
            join(Item.acquisition).\
            outerjoin(Item.cart_item).\
            filter(Item.destroy_time == None,
                   Acquisition.sku == self).\
            filter(or_(Item.cart_item_id == None,
                       CartItem.shipped_time == None)).\
            count()

    @property
    def qty_available(self):
        """
        Quantity of unreserved stock. This query excludes stock associated with
        unshipped orders and active carts.
        """
        return Session.query(Item).\
            join(Item.acquisition).\
            filter(Item.destroy_time == None,
                   Item.cart_item_id == None,
                   Acquisition.sku == self).count()

    def adjust_qty(self, qty_diff, reason, user):
        utcnow = utils.utcnow()
        assert qty_diff != 0
        adj = InventoryAdjustment(
            qty_diff=qty_diff,
            reason=reason,
            user=user,
            acquisition_time=utcnow,
            sku=self,
        )
        Session.add(adj)
        if qty_diff > 0:
            # Add new Item instances.
            for __ in range(qty_diff):
                Session.add(Item(acquisition=adj, create_time=utcnow))
        elif qty_diff < 0:
            # Get the N oldest in-stock items for this SKU to destroy.
            q = Session.query(Item).\
                join(Item.acquisition).\
                outerjoin(Item.cart_item).\
                filter(Acquisition.sku == self).\
                filter(or_(Item.cart_item_id == None,
                           CartItem.shipped_time == None)).\
                filter(Item.destroy_time == None).\
                order_by(Item.id).\
                limit(-qty_diff)
            items = q.all()
            assert len(items) == -qty_diff
            for item in items:
                item.destroy_time = utcnow
        Session.flush()


def sku_for_option_value_ids(product, ov_ids):
    """
    From a list of option value IDs, return the corresponding SKU, or create a
    new one.
    """
    q = Session.query(SKU).filter_by(product=product)
    assert len(ov_ids) == len(product.options), "not enough ov IDs specified"
    for ov_id in ov_ids:
        q = q.filter(SKU.option_values.any(id=ov_id))
    try:
        return q.one()
    except NoResultFound:
        sku = SKU(product=product)
        for ov_id in ov_ids:
            ov = OptionValue.get(ov_id)
            sku.option_values.add(ov)
        Session.add(sku)
        return sku


def sku_for_option_value_ids_sloppy(product, ov_ids):
    """
    From a list of option value IDs, return the corresponding SKU, or create a
    new one. This is the 'sloppy version' that allows for loosely specified
    objects.
    """
    q = Session.query(SKU).filter_by(product=product)
    for ov_id in ov_ids:
        q = q.filter(SKU.option_values.any(id=ov_id))
    sku = q.first()
    if not sku:
        sku = SKU(product=product)
        for ov_id in ov_ids:
            ov = OptionValue.get(ov_id)
            sku.option_values.add(ov)
        Session.add(sku)
    return sku
