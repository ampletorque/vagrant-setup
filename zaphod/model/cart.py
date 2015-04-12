from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

from sqlalchemy import Column, ForeignKey, types, orm
from sqlalchemy.sql import func, or_

from . import custom_types, utils
from .base import Base, Session
from .item import Acquisition, Item

log = logging.getLogger(__name__)


class Cart(Base):
    """
    A user's shopping cart. This object is used for tracking added items prior
    to and after checkout. After checkout, it will be associated with an Order.
    """
    __tablename__ = 'carts'
    id = Column(types.Integer, primary_key=True)
    updated_time = Column(types.DateTime, nullable=False,
                          default=utils.utcnow, index=True,
                          doc='Time this cart was refreshed by a user action.')

    order = orm.relationship('Order', uselist=False, backref='cart')
    items = orm.relationship('CartItem', backref='cart',
                             cascade='all, delete, delete-orphan')

    @property
    def total(self):
        return sum(ci.total for ci in self.items if ci.status != 'cancelled')

    @property
    def items_total(self):
        return sum((ci.price_each * ci.qty_desired) for ci in self.items
                   if ci.status != 'cancelled')

    @property
    def shipping_total(self):
        return sum(ci.shipping_price for ci in self.items
                   if ci.status != 'cancelled')

    @property
    def non_physical(self):
        """
        Return True if this cart is entirely non-physical.
        """
        return all(ci.product.non_physical for ci in self.items)

    @property
    def international_available(self):
        """
        Return True if international shipping is available for all items in
        this cart.
        """
        return all(ci.product.international_available
                   for ci in self.items)

    @property
    def international_surcharge_total(self):
        """
        Return total international shipping price for this cart.
        """
        return sum((ci.product.international_surcharge * ci.qty_desired)
                   for ci in self.items)

    def set_international_shipping(self):
        """
        Set shipping prices for all items in this cart to international
        surcharges.
        """
        for item in self.items:
            item.shipping_price = (item.product.international_surcharge *
                                   item.qty_desired)

    def set_initial_statuses(self):
        """
        Set initial item statuses for a new order.

        For a crowdfunding project, set to 'unfunded' or 'payment pending'
        depending on whether or not the project is successful.

        For a pre-order or stock project, set to 'in process'.
        """
        for item in self.items:
            project = item.product.project
            if item.stage == item.CROWDFUNDING:
                if project.successful:
                    item.update_status('payment pending')
                else:
                    item.update_status('unfunded')
            else:
                item.update_status('in process')

    def refresh(self):
        """
        Refresh item statuses and reservations.
        """
        self.updated_time = utils.utcnow()
        for item in self.items:
            item.refresh()


# These definitions should probably go away and be replaced with only the
# CartItem.x ones.
CROWDFUNDING = 0
PREORDER = 1
STOCK = 2
INACTIVE = 3


class CartItem(Base):
    """
    An item in a user's cart. After checkout, this object is used for tracking
    order fulfillment state.
    """
    __tablename__ = 'cart_items'
    id = Column(types.Integer, primary_key=True)
    cart_id = Column(None, ForeignKey('carts.id'), nullable=False)
    product_id = Column(None, ForeignKey('products.id'),
                        nullable=False)
    sku_id = Column(None, ForeignKey('skus.id'), nullable=False)
    batch_id = Column(None, ForeignKey('batches.id'), nullable=True)
    price_each = Column(custom_types.Money, nullable=False)
    qty_desired = Column(types.Integer, nullable=False, default=1)
    shipping_price = Column(custom_types.Money, nullable=False)

    stage = Column(types.Integer, nullable=False)

    expected_ship_time = Column(types.DateTime, nullable=True)
    shipped_time = Column(types.DateTime, nullable=True)
    shipment_id = Column(None, ForeignKey('shipments.id'), nullable=True)

    status = Column(types.CHAR(16), nullable=False, default='cart')

    product = orm.relationship('Product', backref='cart_items')
    batch = orm.relationship('Batch', backref='cart_items')
    sku = orm.relationship('SKU', backref='cart_items')

    CROWDFUNDING = 0
    PREORDER = 1
    STOCK = 2
    # This is used for carts which have 'expired' without checking out.
    INACTIVE = 3

    available_statuses = [
        ('cart', 'Pre-checkout'),
        ('unfunded', 'Project Not Yet Funded'),
        ('failed', 'Project Failed To Fund'),
        ('waiting', 'Waiting for Items'),
        ('payment pending', 'Payment Not Yet Processed'),
        ('payment failed', 'Payment Failed'),
        ('cancelled', 'Cancelled'),
        ('shipped', 'Shipped'),
        ('abandoned', 'Abandoned'),
        ('in process', 'In Process'),
        ('being packed', 'Being Packed'),
    ]

    @property
    def status_description(self):
        """
        Human-readable description of this item's status.
        """
        return dict(self.available_statuses)[self.status]

    def update_status(self, new_value):
        """
        Update the status of this item. Validates acceptable transitions.
        """
        valid_transitions = {
            'cart': ('unfunded', 'payment pending', 'in process'),
            'unfunded': ('failed', 'cancelled', 'payment pending'),
            'payment pending': ('cancelled', 'waiting', 'payment failed'),
            'payment failed': ('waiting', 'cancelled', 'abandoned'),
            'waiting': ('cancelled', 'in process', 'being packed', 'shipped'),
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
        Calculate the price of this item including selected product option
        values.
        """
        price = self.product.price
        for ov in self.sku.option_values:
            price += ov.price_increase
        return price

    @property
    def total(self):
        """
        Total price of this line item, including shipping.
        """
        return (self.price_each * self.qty_desired) + self.shipping_price

    @property
    def qty_reserved(self):
        """
        Qty of product that is 'reserved' to this order.
        """
        if self.stage == STOCK:
            return Session.query(Item).filter_by(cart_item=self).count()
        else:
            return self.qty_desired

    @property
    def closed(self):
        """
        True if this item is in a final, resolved state.
        """
        return self.status in ('cancelled', 'shipped', 'abandoned', 'failed')

    def release_stock(self):
        """
        Release any reserved stock associated with this item.

        FIXME This is a very naive approach with no protection against race
        conditions.
        """
        q = Session.query(Item).filter_by(cart_item=self)
        for item in q:
            item.cart_item = None
        Session.flush()

    def reserve_stock(self):
        """
        Reserve stock associated with this item.

        FIXME This is a very naive approach with no protection against race
        conditions.
        """
        q = Session.query(Item).\
            join(Item.acquisition).\
            filter(Acquisition.sku == self.sku,
                   Item.destroy_time == None,
                   or_(Item.cart_item == None,
                       Item.cart_item == self)).\
            limit(self.qty_desired)
        items = q.all()
        assert len(items) == self.qty_desired, \
            "only got %d items, wanted %d" % (len(items), self.qty_desired)
        for item in items:
            item.cart_item = self

    def _get_batches_with_lock(self):
        # Read and lock all the batch rows for this product.
        Batch = utils.relationship_class(CartItem.batch)
        return Session.query(Batch).\
            filter_by(product=self.product).\
            with_for_update().\
            all()

    def _refresh_crowdfunding(self):
        log.info('refresh %s: selecting crowdfunding', self.id)
        self.stage = CROWDFUNDING

        if self.product.non_physical:
            self.batch = None
            self.expected_ship_date = None
            log.info('refresh %s: non-physical', self.id)
            return True

        batches = self._get_batches_with_lock()

        # Determine what qty is available, or infinite. Note that this is a bit
        # different from product.qty_claimed because we don't want to clobber
        # reservations for carts that haven't checked out, but are still
        # active.
        cf_consumed = Session.query(func.sum(CartItem.qty_desired)).\
            filter(CartItem.product == self.product,
                   CartItem.id != self.id,
                   CartItem.stage == CartItem.CROWDFUNDING,
                   CartItem.status != 'cancelled').\
            scalar() or 0

        if any(batch.qty is None for batch in batches):
            cf_available = None
        else:
            cf_total = sum(batch.qty for batch in batches)
            cf_available = cf_total - cf_consumed
            log.info('refresh %s: crowdfunding consumed: %s, available: %s',
                     self.id, cf_consumed, cf_available)

        # If less qty is available than desired, bump down desired.
        success = (cf_available is None) or (cf_available >= self.qty_desired)
        if not success:
            self.qty_desired = cf_available
            log.info('refresh %s: reducing crowdfunding qty %s',
                     self.id, cf_available)

        # Allocate pledge batch
        for batch in batches:
            if ((not batch.qty) or
                    ((cf_consumed + self.qty_desired) < batch.qty)):
                self.batch = batch
                log.info('refresh %s: selecting batch %s', self.id, batch.id)
                break
            cf_consumed -= batch.qty

        assert self.batch, "no batch assigned for cart item %s" % self.id
        self.expected_ship_time = self.batch.ship_time
        self.stage = CROWDFUNDING
        log.info('refresh %s: success:%s', self.id, success)
        return success

    def _refresh_non_physical(self):
        self.batch = None
        self.expected_ship_time = None
        self.stage = CartItem.STOCK
        log.info('refresh %s: non-physical', self.id)
        return True

    def _refresh_stock(self):
        # Get up to ``qty_desired`` items that are either unreserved or
        # reserved to this cart item already, with a read lock.
        items_q = Session.query(Item).\
            join(Item.acquisition).\
            filter(Acquisition.sku == self.sku).\
            filter(Item.cart_item == None).\
            filter(Item.destroy_time == None).\
            limit(self.qty_desired).\
            with_for_update()
        items = items_q.all()
        stock_available = len(items)

        assert stock_available > 0, \
            "product flagged as in stock, but no items available"

        log.info('refresh %s: selecting stock', self.id)
        for item in items:
            item.cart_item = self
        if stock_available == self.qty_desired:
            log.info('refresh %s: stock good', self.id)
            partial = False
        else:
            self.qty_desired = stock_available
            log.info('refresh %s: stock partial', self.id)
            partial = True
        self.stage = STOCK
        self.batch = None
        self.expected_ship_time = utils.shipping_day()
        return (not partial)

    def _refresh_preorder(self):
        project = self.product.project

        # Make sure that the product is available.
        accepts_preorders = (project.accepts_preorders and
                             self.product.accepts_preorders)

        if accepts_preorders:
            batches = self._get_batches_with_lock()
            # Determine what qty is available, or infinite. Note that this is a
            # bit different from product.qty_claimed because we don't want to
            # clobber reservations for carts that haven't checked out, but are
            # still active.
            qty_consumed = Session.query(func.sum(CartItem.qty_desired)).\
                filter(CartItem.product == self.product,
                       CartItem.id != self.id,
                       CartItem.stage.in_([CartItem.CROWDFUNDING,
                                           CartItem.PREORDER]),
                       CartItem.status != 'cancelled').\
                scalar() or 0

            if any(batch.qty is None for batch in batches):
                qty_available = None
            else:
                qty_total = sum(batch.qty for batch in batches)
                qty_available = qty_total - qty_consumed
                log.info('refresh %s: cf/preorder consumed: %s, available: %s',
                         self.id, qty_consumed, qty_available)
        else:
            qty_available = 0

        assert (qty_available is None) or (qty_available >= 0)

        # If less qty is available than desired, bump down desired.
        if qty_available == 0:
            self.qty_desired = 0
            self.batch = None
            self.expected_ship_time = None
            log.info('refresh %s: fail, no preorder qty available', self.id)
            return False

        success = ((qty_available is None) or
                   (qty_available >= self.qty_desired))
        if not success:
            self.qty_desired = qty_available
            log.info('refresh %s: reducing preorder qty %s',
                     self.id, qty_available)

        # Allocate pledge batch
        for batch in batches:
            if ((not batch.qty) or
                    ((qty_consumed + self.qty_desired) < batch.qty)):
                self.batch = batch
                log.info('refresh %s: selecting batch %s', self.id, batch.id)
                break
            qty_consumed -= batch.qty

        assert self.batch, "no batch assigned for cart item %s" % self.id
        self.stage = PREORDER
        self.expected_ship_time = self.batch.ship_time
        log.info('refresh %s: success:%s', self.id, success)
        return success

    def refresh(self):
        """
        Refresh status and reservations. For a stock item, ensure that
        qty_reserved is up to date. For a preorder or crowdfunding item,
        allocate to a product batch. Note that since adding this cart item, the
        project may have changed status.

        This method may update .qty_desired, .stage, .batch,
        .expected_ship_time, and associated Item instances.

        Before doing anything, make sure that this cart item has no associated
        order.

        If insufficient qty is available, the .qty_desired will be decremented
        accordingly, and False will be returned. Otherwise, True will be
        returned.
        """
        log.info('refresh %s: begin qty:%s product:%s name:%s',
                 self.id, self.qty_desired, self.product_id, self.product.name)
        assert not self.cart.order, \
            "cannot refresh cart item that has a placed order"
        self.price_each = self.calculate_price()
        project = self.product.project
        self.release_stock()
        if project.status == 'crowdfunding':
            return self._refresh_crowdfunding()
        elif self.product.non_physical:
            return self._refresh_non_physical()
        elif self.product.in_stock:
            return self._refresh_stock()
        else:
            return self._refresh_preorder()

    def expire(self):
        """
        Expire a 'stale' cart item.
        """
        log.info('expire %s', self.id)
        self.batch = None
        self.expected_ship_time = None
        self.release_stock()
        self.stage = INACTIVE
