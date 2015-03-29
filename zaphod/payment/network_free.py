from __future__ import absolute_import, print_function, division

import logging

from .exc import (ProfileNotFoundException, TransactionNotFoundException,
                  TransactionDeclinedException)

log = logging.getLogger(__name__)


class TestPaymentProfile(object):
    def __init__(self, interface, reference, card_number, card_masked,
                 email, description):
        self.interface = interface
        self.reference = reference
        self.card_number = card_number
        self.card_masked = card_masked
        self.email = email
        self.description = description

    def update(self, email=None, description=None):
        if email:
            self.email = email
        if description:
            self.description = description

    def _throw_errors(self):
        if self.card_number == '4000000000000341':
            raise TransactionDeclinedException('testing decline')

    def authorize(self, amount, description, ip, user_agent, referrer):
        "Authorize a transaction, and return a dict with response info."
        self._throw_errors()
        self.interface.transaction_id_counter += 1
        transaction_id = self.interface.transaction_id_counter
        self.interface.transaction_amounts[transaction_id] = amount
        return {
            'avs_address1_result': 'pass',
            'avs_zip_result': 'pass',
            'ccv_result': 'pass',
            'transaction_id': transaction_id,
            'card_type': 'Visa',
        }

    def auth_capture(self, amount, description, ip, user_agent, referrer):
        "Authorize and capture a transaction."
        self._throw_errors()
        return {
            'avs_address1_result': 'pass',
            'avs_zip_result': 'pass',
            'ccv_result': 'pass',
            'card_type': 'Visa'
        }

    def prior_auth_capture(self, amount, transaction_id):
        "Capture a previously authorized transaction by transaction id."
        self._throw_errors()
        if self.interface.transaction_amounts.get(transaction_id, 0) >= amount:
            del self.interface.transaction_amounts[transaction_id]
            return {
                'avs_address1_result': 'pass',
                'avs_zip_result': 'pass',
                'ccv_result': 'pass',
                'card_type': 'Visa',
            }
        else:
            raise TransactionNotFoundException

    def refund(self, amount, transaction_id):
        "Refund a previously captured transaction."
        pass

    def void(self, transaction_id):
        "Void a previously authorized transaction."
        pass


class TestPaymentInterface(object):
    is_test = True

    def __init__(self, credentials=None):
        self.profiles = {}
        self.id_counter = 100
        self.transaction_id_counter = 10000000
        # mapping of transaction ID to amount authorized
        self.transaction_amounts = {}

    def create_profile(self, card_number, exp_year, exp_month, ccv,
                       billing, email=u'', description=u''):
        "Create a new profile, returning a PaymentProfile instance."
        # Make up profile ID and payment profile ID.
        self.id_counter += 1
        reference = self.id_counter
        profile = TestPaymentProfile(
            self,
            reference=reference,
            card_number=card_number,
            card_masked=card_number[-4:],
            email=email,
            description=description)
        self.profiles[reference] = profile
        return profile

    def delete_profile(self, profile):
        "Delete a profile. Accepts a PaymentProfile instance."
        if profile.reference in self.profiles:
            del self.profiles[profile.reference]
        else:
            raise ProfileNotFoundException

    def get_profile(self, reference):
        "Grab a profile by id, returning a PaymentProfile instance."
        if isinstance(reference, int) and reference in self.profiles:
            return self.profiles[reference]
        else:
            raise ProfileNotFoundException
