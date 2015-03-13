from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm

from . import custom_types, utils
from .base import Base, Session
from .item import Item


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

    expected_ship_date = Column(types.DateTime, nullable=True)
    shipped_date = Column(types.DateTime, nullable=True)
    shipment_id = Column(None, ForeignKey('shipments.id'), nullable=True)
    batch_id = Column(None, ForeignKey('batches.id'), nullable=True)
    sku_id = Column(None, ForeignKey('skus.id'), nullable=False)

    status = Column(types.CHAR(16), nullable=False)

    cart = orm.relationship('Cart', backref='items')
    product = orm.relationship('Product', backref='cart_items')
    batch = orm.relationship('Batch', backref='cart_items')
    sku = orm.relationship('SKU', backref='cart_items')

    CROWDFUNDING = 0
    PREORDER = 1
    STOCK = 2

    available_statuses = [
        ('init', 'Unset'),
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
        return dict(self.available_statuses)[self.status]

    def update_status(self, new_value):
        """
        Update the status of this item. Validates acceptable transitions.
        """
        valid_transitions = {
            'unfunded': ('failed', 'cancelled', 'payment pending'),
            'payment pending': ('cancelled', 'waiting', 'payment failed'),
            'payment failed': ('waiting', 'cancelled', 'abandoned'),
            'waiting': ('cancelled', 'in process'),
            'in process': ('cancelled', 'being packed', 'shipped'),
            'being packed': ('shipped',),
        }
        valid_next_statuses = valid_transitions.get(self.status, ())
        assert new_value in valid_next_statuses, \
            "invalid next cart item status: cannot %r -> %r" % (self.status,
                                                                new_value)
        self.status = new_value

    def calculate_price(self):
        """
        Calculate the price of this item.
        """
        price = self.product.price
        for ov in self.sku.option_values:
            price += ov.price_increase
        return price

    @property
    def total(self):
        return (self.price_each + self.shipping_price) * self.qty_desired

    @property
    def qty_reserved(self):
        if self.stage == STOCK:
            return Session.query(Item).filter_by(cart_item=self).count()
        else:
            return self.qty_desired

    @property
    def closed(self):
        return self.status in ('cancelled', 'shipped', 'abandoned', 'failed')

    def release_stock(self):
        # XXX FIXME
        pass

    def refresh(self):
        """
        Refresh status and reservations. For a stock item, ensure that
        qty_reserved is up to date. For a preorder or crowdfunding item,
        allocate to a product batch. Note that since adding this cart item, the
        project may have changed status.

        This method may update .qty_desired, .stage, .batch,
        .expected_ship_date, and associated Item instances.

        Before doing anything, make sure that this cart item has no associated
        order.

        If insufficient qty is available, the .qty_desired will be decremented
        accordingly, and False will be returned. Otherwise, True will be
        returned.
        """
        assert not self.cart.order, \
            "cannot refresh cart item that has a placed order"

        # XXX Lock existing items.

        # XXX The batch allocation needs to take into account qty-- e.g. if
        # there is only a certain qty available in crowdfunding, decrement the
        # qty.

        self.price_each = self.calculate_price()

        project = self.product.project
        if project.status == 'crowdfunding':
            self.stage = CROWDFUNDING
            self.batch = self.product.select_batch(self.qty_desired)
            assert self.batch
            self.expected_ship_date = self.batch.ship_date
            self.release_stock()
            return True
        else:
            # Make sure that the product is available.
            if self.sku.qty_available > self.qty_desired:

                # XXX Reserve stock

                self.stage = STOCK
                self.batch = None
                self.expected_ship_date = utils.shipping_day()
                self.release_stock()
                return True
            elif project.accepts_preorders and self.product.accepts_preorders:
                self.stage = PREORDER
                self.batch = self.product.select_batch(self.qty_desired)
                self.expected_ship_date = self.batch.ship_date
                self.release_stock()
                return True
            else:
                # This thing is no longer available.
                self.qty_desired = 0
                self.batch = None
                self.expected_ship_date = None
                self.release_stock()
                return False
