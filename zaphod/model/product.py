from datetime import datetime
from decimal import Decimal

from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint, types, orm
from sqlalchemy.sql import func
from sqlalchemy.ext.orderinglist import ordering_list

from pyramid_es.mixin import ElasticMixin, ESMapping, ESField, ESString

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
    ship_time = Column(types.DateTime, nullable=False)

    @property
    def qty_claimed(self):
        # XXX performance
        # XXX Should this exclude cancelled or fraudulent orders?
        return Session.query(func.sum(CartItem.qty_desired)).\
            filter(CartItem.batch == self).\
            filter(CartItem.status != 'cancelled').\
            scalar() or 0


associated_products_table = Table(
    'associated_products',
    Base.metadata,
    Column('source_id', None, ForeignKey('products.id'),
           primary_key=True),
    Column('dest_id', None, ForeignKey('products.id'),
           primary_key=True),
    mysql_engine='InnoDB')


class Product(Base, ImageMixin, ElasticMixin):
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
                             default=Decimal('2.75'))

    hs_code = Column(types.String(255), nullable=False, default=u'')
    # In kg
    shipping_weight = Column(types.Float, nullable=False, default=0)
    # In cm
    box_length = Column(types.Float, nullable=False, default=0)
    box_width = Column(types.Float, nullable=False, default=0)
    box_height = Column(types.Float, nullable=False, default=0)

    batches = orm.relationship('Batch', backref='product',
                               order_by='Batch.ship_time')

    options = orm.relationship(
        'Option',
        backref='product',
        collection_class=ordering_list('gravity'),
        order_by='Option.gravity',
    )
    published_options = orm.relationship(
        'Option',
        primaryjoin=('and_(Option.product_id == Product.id,'
                     'Option.published == True)'),
        order_by='Option.gravity',
        viewonly=True,
    )

    associated_products = orm.relationship(
        'Product',
        secondary=associated_products_table,
        collection_class=set,
        primaryjoin='associated_products.c.source_id == Product.id',
        secondaryjoin='associated_products.c.dest_id == Product.id',
    )

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
    def current_ship_time(self):
        """
        Return the delivery date for the currently 'open' batch.
        """
        return self.current_batch.ship_time

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
        # XXX Should this exclude other item statuses?
        return Session.query(func.sum(CartItem.qty_desired)).\
            join(CartItem.cart).\
            join(Cart.order).\
            filter(CartItem.product == self).\
            filter(CartItem.stage.in_([CartItem.CROWDFUNDING,
                                       CartItem.PREORDER])).\
            filter(CartItem.status != 'cancelled').\
            scalar() or 0

    @property
    def is_available(self):
        return self.non_physical or self.in_stock or bool(self.current_batch)

    def calculate_in_stock(self):
        return any(sku.qty_available > 0 for sku in self.skus)

    def update_in_stock(self):
        self.in_stock = self.calculate_in_stock()

    def validate_schedule(self):
        """
        Validate this product's production schedule.
        """
        assert self.batches, "schedule must have at least one batch"

        last_time = datetime(1970, 1, 1)
        for ii, batch in enumerate(self.batches, start=1):
            assert batch.ship_time > last_time, \
                "batch dates must monotonically increase"
            if batch.qty is None:
                assert ii == len(self.batches), \
                    "only the last batch can have infinite qty"
            else:
                assert batch.qty > 0, \
                    "batch qty must be greater than zero"

    @classmethod
    def elastic_mapping(cls):
        return ESMapping(
            analyzer='content',
            properties=ESMapping(
                ESField('id'),
                ESString('name'),
                project=ESMapping(
                    properties=ESMapping(
                        ESString('name', boost=4),
                    ),
                ),
            ))


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

    values = orm.relationship(
        'OptionValue',
        backref='option',
        collection_class=ordering_list('gravity'),
        order_by='OptionValue.gravity',
    )
    published_values = orm.relationship(
        'OptionValue',
        primaryjoin=('and_(OptionValue.option_id == Option.id,'
                     'OptionValue.published == True)'),
        viewonly=True,
        order_by='OptionValue.gravity',
    )

    def __repr__(self):
        return '<Option(id=%r, name=%r)>' % (self.id, self.name)

    @property
    def default_value(self):
        for ov in self.values:
            if ov.is_default:
                return ov


class OptionValue(Base):
    """
    A single possible 'choice' for an option.
    """
    __tablename__ = 'option_values'
    __table_args__ = (UniqueConstraint('option_id', 'is_default'),
                      {'mysql_engine': 'InnoDB'})
    id = Column(types.Integer, primary_key=True)
    option_id = Column(None, ForeignKey('options.id'), nullable=False)
    description = Column(types.Unicode(255), nullable=False, default=u'')
    price_increase = Column(custom_types.Money, nullable=False, default=0)
    gravity = Column(types.Integer, nullable=False, default=0)
    is_default = Column(types.Boolean, nullable=True)
    published = Column(types.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<OptionValue(id=%r, description=%r)>' % (self.id,
                                                         self.description)
