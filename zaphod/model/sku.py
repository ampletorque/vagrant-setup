from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Table, Column, ForeignKey, types, orm
from sqlalchemy.orm.exc import NoResultFound

from .base import Base, Session
from .product import OptionValue


sku_option_values = Table(
    'sku_option_values',
    Base.metadata,
    Column('sku_id', None, ForeignKey('skus.id'), primary_key=True),
    Column('option_value_id', None, ForeignKey('option_values.id'),
           primary_key=True),
    mysql_engine='InnoDB')


class SKU(Base):
    __tablename__ = 'skus'
    __table_args__ = {'mysql_engine': 'InnoDB'}
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
        # XXX
        return 0

    @property
    def qty_available(self):
        """
        Quantity of unreserved stock. This query excludes stock associated with
        unshipped orders and active carts.
        """
        # XXX
        return 0


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
