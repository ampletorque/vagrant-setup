from __future__ import absolute_import, print_function, division

from .exc import (ProfileNotFoundException, TransactionNotFoundException,
                  TransactionDeclinedException)


class TestPaymentProfile(object):
    def __init__(self, interface, reference, card_number, card_masked,
                 customer_id, email, description):
        self.interface = interface
        self.reference = reference
        self.card_number = card_number
        self.card_masked = card_masked
        self.customer_id = customer_id
        self.email = email
        self.description = description

    def update(self, **kwargs):
        for key in ['customer_id', 'email', 'description']:
            kwargs.setdefault(key, getattr(self, key))
            setattr(self, key, kwargs[key])

    def _throw_errors(self):
        if self.card_number == '4000000000000341':
            raise TransactionDeclinedException('testing decline')

    def authorize(self, amount, invoice_number, ccv=None):
        "Authorize a transaction, and return a dict with response info."
        self._throw_errors()
        self.interface.transaction_id_counter += 1
        transaction_id = self.interface.transaction_id_counter
        self.interface.transaction_amounts[transaction_id] = amount
        if ccv:
            ccv_result = 'M'
        else:
            ccv_result = ''
        return {'approval_code': 'aaaaaa',
                'avs_result': 'Y',
                'ccv_result': ccv_result,
                'transaction_id': transaction_id,
                'card_type': 'Visa'}

    def capture(self, amount, invoice_number, approval_code, ccv=None):
        "Capture a transaction, using approval code only. Returns nothing."
        self._throw_errors()

    def auth_capture(self, amount, invoice_number, ccv=None):
        "Authorize and capture a transaction."
        self._throw_errors()
        if ccv:
            ccv_result = 'M'
        else:
            ccv_result = ''
        return {'avs_result': 'Y',
                'ccv_result': ccv_result,
                'card_type': 'Visa'}

    def prior_auth_capture(self, amount, invoice_number, transaction_id):
        "Capture a previously authorized transaction by transaction id."
        self._throw_errors()
        if self.interface.transaction_amounts.get(transaction_id, 0) >= amount:
            del self.interface.transaction_amounts[transaction_id]
            return {'avs_result': 'Y',
                    'ccv_result': '',
                    'card_type': 'Visa'}
        else:
            raise TransactionNotFoundException

    def refund(self, amount, invoice_number, transaction_id):
        "Refund a previously captured transaction."
        pass

    def void(self, transaction_id):
        "Void a previously authorized transaction."
        pass


class TestPaymentInterface(object):
    allows_auth_only = True
    allows_server_side_profile = True
    is_test = True
    is_paypal = False

    def __init__(self, credentials=None):
        self.profiles = {}
        self.id_counter = 100
        self.transaction_id_counter = 10000000
        # mapping of transaction ID to amount authorized
        self.transaction_amounts = {}

    def _mask_card(self, card_number):
        return 'XXXX' + card_number[-4:]

    def _strip_spaces(self, card_number):
        return card_number.replace(' ', '').replace('\t', '')

    def create_profile(self, card_number, expiration_date,
                       ccv, billing, customer_id, email=u'',
                       description=u''):
        "Create a new profile, returning a PaymentProfile instance."
        # Make up profile ID and payment profile ID.
        self.id_counter += 1
        reference = self.id_counter
        profile = TestPaymentProfile(
            self,
            reference=reference,
            card_number=self._strip_spaces(card_number),
            card_masked=self._mask_card(card_number),
            customer_id=customer_id,
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
