from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import timedelta

from sqlalchemy import Column, ForeignKey, types, orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property, validates
from sqlalchemy.sql import and_

from . import custom_types, utils
from .base import Base
from .address import make_address_columns


class PaymentGateway(Base):
    """
    A payment gateway, which can have payments made against it. Tracks the
    credentials used to authenticate to the upstream provider and make a given
    payment.
    """
    __tablename__ = 'payment_gateways'
    id = Column(types.Integer, primary_key=True)
    dev = Column(types.Boolean, nullable=False)
    enabled = Column(types.Boolean, nullable=False)
    comment = Column(types.Unicode(255), nullable=False, default=u'')
    interface = Column(types.String(255), nullable=False)
    credentials = Column(custom_types.JSON(255), nullable=False)
    parent_id = Column(None, ForeignKey('payment_gateways.id'), nullable=True)

    # This is a mechanism to support payment gateways which are 'dependent' on
    # another gateway, for example, Stripe Connect users.
    # If a parent is specified:
    #   - Don't load profile information directly: instead, load it through the
    #     parent gateway.
    #   - Describe the payment method in terms of its information *and* the
    #     child gateway.
    #   - Don't show the payment method on a customer-facing website.
    parent = orm.relationship('PaymentGateway', remote_side=[id])


class PaymentMethod(Base):
    """
    A stored payment method belonging to a user. Payments can be made on this
    method.
    """
    __tablename__ = 'payment_methods'
    id = Column(types.Integer, primary_key=True)
    user_id = Column(None, ForeignKey('users.id'), nullable=True)
    payment_gateway_id = Column(None, ForeignKey('payment_gateways.id'),
                                nullable=False)
    save = Column(types.Boolean, nullable=False, default=False)
    reference = Column(custom_types.JSON(255), nullable=False)
    billing = make_address_columns('billing')
    # True for payment methods created with Stripe.js, False otherwise.
    stripe_js = Column(types.Boolean, nullable=False)
    # Note that this is a long string so that it works for IPv6 addresses,
    # which can be up to 45 characters.
    remote_addr = Column(types.String(50), nullable=True)
    user_agent = Column(types.Unicode(255), nullable=True)
    session_id = Column(types.String(255), nullable=True)

    user = orm.relationship('User', backref='payment_methods')
    gateway = orm.relationship('PaymentGateway')


class StateMixin(object):
    """
    Use as a mixin to add basic state transitioning method.
    """
    def transition(self, name, checkfunc, user):
        assert checkfunc()
        setattr(self, '%s_time' % name, utils.utcnow())
        setattr(self, '%s_by' % name, user)


class Payment(Base, StateMixin):
    """
    A payment object corresponding to some amount of debit or credit on an
    order. This class cannot be instantiated directly, but is subclassed.
    """
    __tablename__ = 'payments'
    id = Column(types.Integer, primary_key=True)
    order_id = Column(None, ForeignKey('orders.id'), nullable=False)
    created_by_id = Column(None, ForeignKey('users.id'), nullable=False)
    amount = Column(custom_types.Money, nullable=False)
    transaction_fee = Column(custom_types.Money, nullable=False, default=0)
    created_time = Column(types.DateTime, nullable=False,
                          default=utils.utcnow)
    voided_time = Column(types.DateTime, nullable=True)
    voided_by_id = Column(None, ForeignKey('users.id'), nullable=True)
    pending_action_time = Column(types.DateTime, nullable=True)
    pending_action_by_id = Column(None, ForeignKey('users.id'),
                                  nullable=True)
    pending_action = Column(types.String(4), nullable=False, default=u'')
    comments = Column(types.UnicodeText, nullable=False, default=u'')
    discriminator = Column(types.String(4), nullable=False)
    __mapper_args__ = {'polymorphic_on': discriminator}

    order = orm.relationship('Order', backref='payments')
    created_by = orm.relationship(
        'User',
        primaryjoin='User.id == Payment.created_by_id')
    voided_by = orm.relationship(
        'User',
        primaryjoin='User.id == Payment.voided_by_id')
    pending_action_by = orm.relationship(
        'User',
        primaryjoin='User.id == Payment.pending_action_by_id')

    @hybrid_property
    def valid(self):
        return self.voided_time == None

    def can_be_voided(self):
        void_time = self.created_time + timedelta(hours=1)
        return self.valid and utils.utcnow() < void_time

    def mark_as_void(self, user):
        self.transition('voided', self.can_be_voided, user)

    @property
    def refundable_amount(self):
        if not self.valid:
            return 0
        return self.amount


class CashPayment(Payment):
    "Just a cash payment, no extra columns."
    __mapper_args__ = {'polymorphic_identity': 'cash'}


class CheckPayment(Payment):
    """
    A Check payment.

    Checks may be marked as void or bounced.
    """
    __tablename__ = 'check_payments'
    payment_id = Column(None, ForeignKey('payments.id'), primary_key=True)
    reference = Column(types.Unicode(50), nullable=False, default=u'')
    check_date = Column(types.Date, nullable=False)
    bounced_time = Column(types.DateTime, nullable=True)
    bounced_by_id = Column(None, ForeignKey('users.id'), nullable=True)

    bounced_by = orm.relationship(
        'User',
        primaryjoin='User.id == CheckPayment.bounced_by_id')

    __mapper_args__ = {'polymorphic_identity': 'chck'}

    @hybrid_property
    def valid(self):
        return self.voided_time == None and self.bounced_time == None

    def can_be_bounced(self):
        return self.valid

    def mark_as_bounced(self, user):
        self.transition('bounced', self.can_be_bounced, user)


class CreditCardPayment(Payment):
    """
    A Credit Card payment.

    The payment must be authorized before this object is created. Refunds
    (credits) are represented with this class by creating a second object with
    a negative amount and the same transaction_id as the transaction being
    credited against.
    """
    __tablename__ = 'credit_card_payments'
    payment_id = Column(None, ForeignKey('payments.id'), primary_key=True)
    transaction_id = Column(types.Unicode(50), nullable=False)
    invoice_number = Column(types.Unicode(50), nullable=False)
    authorized_amount = Column(custom_types.Money, nullable=False)
    # Single-character AVS result code as returned by authorize.net, can be
    # decoded with the method below.
    avs_result = Column(types.String(1), nullable=False, default='')
    ccv_result = Column(types.String(1), nullable=False, default='')
    captured_time = Column(types.DateTime, nullable=True)
    captured_state = Column(types.String(2), nullable=False, default='un')
    transaction_error_time = Column(types.DateTime, nullable=True)
    transaction_error = Column(types.Unicode(50), nullable=False, default=u'')
    chargeback_time = Column(types.DateTime, nullable=True)
    chargeback_by_id = Column(None, ForeignKey('users.id'), nullable=True)
    # NOTE: Don't set this directly, use .card_type instead.
    card_type_code = Column(types.String(1), nullable=False, default='U')
    expired = Column(types.Boolean, nullable=False, default=False)
    # Possible states are open, won, lost.
    chargeback_state = Column(types.String(4), nullable=True)

    chargeback_by = orm.relationship(
        'User',
        primaryjoin='User.id == CreditCardPayment.chargeback_by_id')

    payment_method_id = Column(None, ForeignKey('payment_methods.id'),
                               nullable=False)
    method = orm.relationship('PaymentMethod', backref='payments')
    __mapper_args__ = {'polymorphic_identity': 'cc'}

    can_be_captured = column_property(
        and_(Payment.voided_time == None,
             expired == False,
             captured_state == 'un'))

    @hybrid_property
    def marked_for_capture(self):
        return ((self.pending_action_time != None) &
                (self.pending_action == 'capt') &
                (self.captured_state == 'un'))

    @hybrid_property
    def marked_for_voiding(self):
        return ((self.pending_action_time != None) &
                (self.pending_action == 'void') &
                (self.voided_time == None))

    @property
    def is_first_payment(self):
        return self.method.first_payment == self

    card_type_codes = [('A', 'American Express'),
                       ('M', 'MasterCard'),
                       ('V', 'Visa'),
                       ('D', 'Discover'),
                       ('P', 'Paypal'),
                       ('U', 'Unknown')]

    @hybrid_property
    def card_type(self):
        return dict(self.card_type_codes)[self.card_type_code]

    @card_type.setter
    def card_type(self, value):
        codes = {k: v for v, k in self.card_type_codes}
        self.card_type_code = codes.get(value, 'U')

    def __init__(self, *args, **kwargs):
        card_type = kwargs.pop('card_type', '')
        Payment.__init__(self, *args, **kwargs)
        self.card_type = card_type

    @hybrid_property
    def valid(self):
        # Note: this should probably check for chargeback status, but doesn't
        # at the moment.
        return (self.voided_time == None and
                self.expired == False and
                self.pending_action != "void")

    def can_be_voided(self):
        return self.valid and not self.captured_time

    def mark_for_voiding(self, user):
        self.transition('pending_action', self.can_be_voided, user)
        self.pending_action = 'void'

    def mark_as_void(self, user):
        self.transition('voided', self.can_be_marked_as_void, user)

    def can_be_marked_as_void(self):
        return (not self.voided_time and not self.chargeback_time and
                not self.expired and not self.captured_time)

    def can_be_marked_as_captured(self):
        return (not self.captured_time and
                not self.voided_time and
                not self.expired)

    def mark_for_capture(self, user):
        "Flags a payment for pending capture."
        self.transition('pending_action', self.can_be_marked_as_captured,
                        user)
        self.pending_action = 'capt'

    def mark_as_captured(self, user, amount):
        "Marks a payment as captured."
        self.transition('captured', self.can_be_marked_as_captured, user)
        self.amount = amount
        self.captured_state = 'ca'

    def can_be_charged_back(self):
        return (self.captured_state in ('ca', 'er') and
                not self.chargeback_time)

    def mark_as_chargeback(self, user):
        self.transition('chargeback', self.can_be_charged_back, user)
        self.chargeback_state = 'open'

    def can_be_marked_as_expired(self):
        return self.can_be_marked_as_captured()

    @property
    def refunded_amount(self):
        return sum(refund.refund_amount for refund in self.refunds
                   if refund.valid)

    @property
    def refundable_amount(self):
        # Credit card payments less than 120 days old can be refunded with a
        # credit card refund.
        # NOTE: This cutoff really could be compared against
        # payment.captured_time, but since we allow users to manually mark
        # payments as captured, the capture time is not reliable.# To be more
        # conservative, we use the auth time instead.
        age_cutoff = utils.utcnow() - timedelta(days=120)
        if (not self.valid) or (self.created_time < age_cutoff):
            return 0
        return self.amount + self.refunded_amount


class Refund(Payment):
    "A refund."
    __tablename__ = 'refunds'
    payment_id = Column(None, ForeignKey('payments.id'), primary_key=True)

    # Authorized refund amount. Refund.amount is updated when the refund is
    # actually executed.
    refund_amount = Column(custom_types.Money, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'rfnd'}

    payment_type = None

    @validates('refund_amount')
    def validates_refund_amount(self, k, v):
        assert v < 0
        return v


class CashRefund(Refund):
    __mapper_args__ = {'polymorphic_identity': 'carf'}

    payment_type = CashPayment


class CheckRefund(Refund):
    "A Check refund."
    __tablename__ = 'check_refunds'
    __mapper_args__ = {'polymorphic_identity': 'chrf'}

    refund_id = Column(None, ForeignKey('refunds.payment_id'),
                       primary_key=True)
    reference = Column(types.Integer, nullable=True)

    payment_type = CheckPayment


class CreditCardRefund(Refund):
    "A Credit Card refund."
    __tablename__ = 'credit_card_refunds'
    refund_id = Column(
        None, ForeignKey('refunds.payment_id'), primary_key=True)
    credit_card_payment_id = Column(
        None, ForeignKey('credit_card_payments.payment_id'), nullable=False)

    processed_time = Column(types.DateTime, nullable=True)
    processed_by_id = Column(None, ForeignKey('users.id'), nullable=True)

    transaction_error_time = Column(types.DateTime, nullable=True)
    transaction_error = Column(types.Unicode(50), nullable=False, default=u'')

    credit_card_payment = orm.relationship('CreditCardPayment',
                                           backref='refunds')

    payment_type = CreditCardPayment

    processed_by = orm.relationship(
        'User',
        primaryjoin='User.id == CreditCardRefund.processed_by_id')

    def can_be_voided(self):
        if not self.processed_time and not self.voided_time:
            return True
        return False

    def mark_as_void(self, user):
        self.transition('voided', self.can_be_voided, user)

    def can_be_processed(self):
        return self.valid and not self.processed_time

    def mark_for_processing(self, user, amount):
        "Flags a refund for pending action"
        self.transition('pending_action', self.can_be_processed, user)
        self.pending_action = 'rfnd'
        self.refund_amount = amount

    def mark_as_processed(self, user, amount):
        "Marks refund as processed."
        self.transition('processed', self.can_be_processed, user)
        self.amount = amount

    __mapper_args__ = {'polymorphic_identity': 'ccrf'}
