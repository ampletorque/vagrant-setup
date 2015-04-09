from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import random
import string

from pyramid.settings import asbool

from .. import model

from .exc import UnknownGatewayException
from .mock import MockPaymentInterface
from .stripe import StripeInterface


def get_payment_interface(registry, gateway_id):
    settings = registry.settings
    if not hasattr(registry, 'payment_interfaces'):
        registry.payment_interfaces = {}
    payment_interfaces = registry.payment_interfaces
    if gateway_id not in payment_interfaces:
        gw = model.Session.query(model.PaymentGateway).\
            filter_by(dev=(asbool(settings.get('debug')) or
                           asbool(settings.get('testing'))),
                      enabled=True,
                      id=gateway_id).first()
        if asbool(settings.get('payment.mock')):
            iface = MockPaymentInterface()
        elif gw is None:
            raise UnknownGatewayException()
        else:
            iface = StripeInterface(gw.credentials)
        payment_interfaces[gateway_id] = iface
    return payment_interfaces[gateway_id]


def get_masked_card(registry, payment_method):
    gw = payment_method.gateway
    gateway_id = gw.parent_id or gw.id
    interface = get_payment_interface(registry, gateway_id)
    profile = interface.get_profile(payment_method.reference)
    return profile.card_masked


def make_descriptor(registry, description):
    """
    Make a descriptor, up to 22 chars, to be used for a payment of a given
    project.
    """
    chars = string.ascii_uppercase + string.digits
    random_code = ''.join(random.choice(chars) for __ in range(3))
    s = 'CROWDSUPPLY %s %s' % (random_code, description)
    return s.upper()[:22]
