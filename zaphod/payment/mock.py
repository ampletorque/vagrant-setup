import logging

import binascii
import os

from .exc import (ProfileNotFoundException, TransactionNotFoundException,
                  TransactionDeclinedException)

log = logging.getLogger(__name__)


class MockTransaction(object):
    def __init__(self, id, profile, amount, description,
                 ip, user_agent, referrer):
        self.id = binascii.hexlify(os.urandom(16))
        self.profile = profile
        self.amount = amount
        self.description = description
        self.ip = ip
        self.user_agent = user_agent
        self.referrer = referrer

        if self.profile.card_number == '4000000000000341':
            raise TransactionDeclinedException('test card decline')

        self.avs_address1_result = 'pass'
        self.avs_zip_result = 'pass'
        self.ccv_result = 'pass'
        self.card_type = 'Visa'

        self.state = 'authorized'

    def capture(self):
        if self.state != 'authorized':
            raise TransactionNotFoundException
        else:
            self.state = 'captured'

    def void(self):
        if self.state != 'authorized':
            raise TransactionNotFoundException
        else:
            self.state = 'void'


class MockPaymentProfile(object):
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

    def authorize(self, amount, description, ip, user_agent, referrer):
        "Authorize a transaction, and return a dict with response info."
        transaction = MockTransaction(
            profile=self,
            amount=amount,
            description=description,
            ip=ip,
            user_agent=user_agent,
            referrer=referrer,
        )
        self.interface.transactions[transaction.id] = transaction
        return {
            'transaction_id': transaction.id,
            'avs_address1_result': transaction.avs_address1_result,
            'avs_zip_result': transaction.avs_zip_result,
            'ccv_result': transaction.ccv_result,
            'card_type': transaction.card_type,
        }

    def auth_capture(self, amount, description, ip, user_agent, referrer):
        "Authorize and capture a transaction."
        transaction = MockTransaction(
            profile=self,
            amount=amount,
            description=description,
            ip=ip,
            user_agent=user_agent,
            referrer=referrer,
        )
        self.interface.transactions[transaction.id] = transaction
        return {
            'transaction_id': transaction.id,
            'avs_address1_result': transaction.avs_address1_result,
            'avs_zip_result': transaction.avs_zip_result,
            'ccv_result': transaction.ccv_result,
            'card_type': transaction.card_type,
        }

    def prior_auth_capture(self, amount, transaction_id):
        "Capture a previously authorized transaction by transaction id."
        transaction = self.interface.transactions[transaction_id]
        transaction.capture()
        return {
            'transaction_id': transaction.id,
            'avs_address1_result': transaction.avs_address1_result,
            'avs_zip_result': transaction.avs_zip_result,
            'ccv_result': transaction.ccv_result,
            'card_type': transaction.card_type,
        }

    def refund(self, amount, transaction_id):
        "Refund a previously captured transaction."
        transaction = self.interface.transactions[transaction_id]
        transaction.refund()

    def void(self, transaction_id):
        "Void a previously authorized transaction."
        transaction = self.interface.transactions[transaction_id]
        transaction.void()


class MockPaymentInterface(object):
    def __init__(self, credentials=None):
        self.profiles = {}
        self.transactions = {}
        self.id_counter = 100

    def create_profile(self, card_number, exp_year, exp_month, ccv,
                       billing, email=u'', description=u''):
        "Create a new profile, returning a PaymentProfile instance."
        # Make up profile ID and payment profile ID.
        self.id_counter += 1
        reference = self.id_counter
        profile = MockPaymentProfile(
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
        if reference in self.profiles:
            return self.profiles[reference]
        else:
            raise ProfileNotFoundException
