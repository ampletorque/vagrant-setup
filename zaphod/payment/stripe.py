from __future__ import absolute_import, print_function, division

import logging

from decimal import Decimal

import stripe

from . import exc

log = logging.getLogger(__name__)


class StripeInterface(object):
    def __init__(self, credentials):
        self.api_key = credentials['api_key']
        self.prefix = credentials.get('prefix')
        self.log = logging.LoggerAdapter(log, {'login': self.api_key})

    def _wrap_call(self, f, *args, **kwargs):
        try:
            return f(*args, api_key=self.api_key, **kwargs)
        except stripe.CardError as e:
            # A decline
            body = e.json_body
            err = body['error']
            # e.http_status
            # err['type']
            # err['code']
            # err['param']
            # err['message']
            new_e = exc.TransactionDeclinedException(
                'The transaction was declined: %r' % err)
            new_e.original_exception = e
            new_e.error = err
            raise new_e

        except stripe.AuthenticationError as e:
            new_e = exc.AuthenticationException()
            new_e.original_exception = e
            raise new_e

        except stripe.InvalidRequestError as e:
            new_e = exc.ParameterException()
            new_e.original_exception = e
            raise new_e

        except (stripe.APIConnectionError, stripe.StripeError) as e:
            new_e = exc.PaymentException()
            new_e.original_exception = e
            raise new_e

    def create_profile(self, card_number, exp_year, exp_month, ccv,
                       billing, email=u'', description=u''):
        """
        Create a new profile, returning a PaymentProfile instance.
        """
        self.log.info("create_profile\email:%s", email)
        name = "%s %s" % (billing.first_name, billing.last_name)

        if self.prefix:
            description = '%s:%s' % (self.prefix, description)

        cu = self._wrap_call(
            stripe.Customer.create,
            description=description,
            email=email,
            card=dict(number=card_number,
                      exp_month=exp_month,
                      exp_year=exp_year,
                      cvc=ccv,
                      name=name,
                      description=description,
                      email=email,
                      address_line1=billing.address1,
                      address_zip=billing.postal_code,
                      address_state=billing.state.upper(),
                      address_country=billing.country_name.upper()))
        self.log.info("create_profile response:\n%r", cu)

        return StripePaymentProfile(customer_id=cu.id,
                                    customer=cu,
                                    interface=self)

    def delete_profile(self, profile):
        """
        Delete a profile. Accepts a PaymentProfile instance.
        """
        customer_id = profile.reference['customer_id']
        self.log.info("delete_profile\tcustomer_id:%s", customer_id)
        cu = self._wrap_call(
            stripe.Customer.retrieve,
            customer_id)
        resp = cu.delete()
        self.log.info("delete_profile response:\n%r", resp)

    def get_profile(self, reference):
        """
        Grab a profile by id, returning a PaymentProfile instance.
        """
        customer_id = reference['customer_id']
        return StripePaymentProfile(customer_id=customer_id, interface=self)


class StripePaymentProfile(object):
    def __init__(self, customer_id, interface, customer=None):
        self.customer_id = customer_id
        self.interface = interface
        self.customer = customer
        self.api_key = self.interface.api_key

    def _load_customer(self):
        if not self.customer:
            self.interface.log.debug("_load_customer\tcustomer_id:%s",
                                     self.customer_id)
            self.customer = stripe.Customer.retrieve(
                self.customer_id,
                api_key=self.api_key)
            self.interface.log.debug("_load_customer response:\n%r",
                                     self.customer)
        else:
            self.interface.log.debug(
                "_load_customer\tcustomer_id:%s already loaded",
                self.customer.id)

    @property
    def card_masked(self):
        self._load_customer()
        active_card = self.customer.active_card
        return active_card['last4']

    @property
    def avs_address1_result(self):
        return self.customer.active_card.address_line1_check

    @property
    def avs_zip_result(self):
        return self.customer.active_card.address_zip_check

    @property
    def ccv_result(self):
        return self.customer.active_card.ccv_check

    def _to_cents(self, amount):
        # XXX assert that the amount has non-fractional cents
        assert isinstance(amount, Decimal)
        amount = amount * 100
        just_cents = amount.quantize(Decimal(1))
        assert amount == just_cents
        return amount

    def _charge_status(self, charge):
        return {
            'avs_address1_result': charge.card.address_line1_check,
            'avs_zip_result': charge.card.address_zip_check,
            'ccv_result': charge.card.ccv_check,
        }

    def update(self, **kwargs):
        self.interface.log.info("update\tcustomer_id:%s\tkw:%r",
                                self.customer_id, kwargs)
        self._load_customer()
        if "customer_id" in kwargs:
            raise NotImplementedError('updating customer_id is not allowed')

        for key in ['email', 'description']:
            if key in kwargs:
                setattr(self.customer, key, kwargs[key])
        resp = self.customer.save()
        self.interface.log.info("update\tresponse:\n%r", resp)

    def authorize(self, amount, description, ip, user_agent, referrer):
        """
        Authorize a transaction, and return a dict with response info.
        """
        self.interface.log.info("authorize\tcustomer_id:%s\t"
                                "amount:%0.2f\tdescription:%s",
                                self.customer_id, amount, description)
        amount_cents = self._to_cents(amount)
        assert amount_cents > 50, "can't make a charge for less than $0.50"

        if self.interface.prefix:
            description = '%s:%s' % (self.interface.prefix, description)

        charge = self.interface._wrap_call(
            stripe.Charge.create,
            amount=amount_cents,
            currency='usd',
            customer=self.customer_id,
            description=description,
            capture=False,
            ip=ip,
            user_agent=user_agent,
            referrer=referrer,
            payment_user_agent='Crowd Supply Web Platform',
        )

        self.interface.log.info("authorize response:\n%r", charge)

        return dict(
            transaction_id=charge.id,
            **self._charge_status(charge))

    def prior_auth_capture(self, amount, transaction_id):
        """
        Capture a previously authorized transaction by transaction id.
        """
        self.interface.log.info("prior_auth_capture\tcustomer_id:%s\t"
                                "amount:%0.2f\ttransaction_id:%s",
                                self.customer_id, amount,
                                transaction_id)

        charge = self.interface._wrap_call(
            stripe.Charge.retrieve,
            transaction_id)
        resp = charge.capture()

        self.interface.log.info("prior_auth_capture response:\n%r", resp)

        return self._charge_status(resp)

    def auth_capture(self, amount, description, ip, user_agent, referrer):
        """
        Authorize and capture a transaction.
        """
        self.interface.log.info("auth_capture\tcustomer_id:%s\t"
                                "amount:%0.2f\tdescription:%s\t",
                                self.customer_id, amount, description)
        amount_cents = self._to_cents(amount)
        assert amount_cents > 50, "can't make a charge for less than $0.50"

        if self.interface.prefix:
            description = '%s:%s' % (self.interface.prefix, description)

        charge = self.interface._wrap_call(
            stripe.Charge.create,
            amount=amount_cents,
            currency='usd',
            customer=self.customer_id,
            description=description,
            ip=ip,
            user_agent=user_agent,
            referrer=referrer,
            payment_user_agent='Crowd Supply Web Platform',
        )

        self.interface.log.info("auth_capture response:\n%r", charge)

        return dict(
            transaction_id=charge.id,
            approval_code="",
            **self._charge_status(charge))

    def refund(self, amount, transaction_id):
        """
        Refund a previously captured transaction.
        """
        self.interface.log.info("refund\tcustomer_id:%s\tamount:%0.2f\t"
                                "transaction_id:%s",
                                self.customer_id, amount, transaction_id)

        charge = self.interface._wrap_call(
            stripe.Charge.retrieve,
            transaction_id)

        fees = {}
        for fee_detail in charge.fee_details:
            fees[fee_detail.type] = fee_detail.amount

        if 'application_fee' in fees:
            resp = charge.refund(amount=self._to_cents(amount),
                                 refund_application_fee=True)
        else:
            resp = charge.refund(amount=self._to_cents(amount))

        self.interface.log.info("refund response:\n%r", resp)

    def void(self, transaction_id):
        """
        Void a previously authorized transaction.
        """
        self.interface.log.info("void\tcustomer_id:%s\ttransaction_id:%s",
                                self.customer_id, transaction_id)

        charge = self.interface._wrap_call(
            stripe.Charge.retrieve,
            transaction_id)
        resp = charge.refund()

        self.interface.log.info("void response:\n%r", resp)
