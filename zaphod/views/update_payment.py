from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import socket

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.settings import asbool
from pyramid_uniform import Form, FormRenderer
from formencode import Schema, NestedVariables, validators
from itsdangerous import TimestampSigner

from .. import model, payment, custom_validators
from ..payment.exc import PaymentException

log = logging.getLogger(__name__)


class UpdatePaymentForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    cc = custom_validators.SelectValidator(
        {'yes': validators.Constant('saved')},
        default=custom_validators.CreditCardSchema(),
        selector_field='use_saved')


class UpdatePaymentView(object):
    def __init__(self, request):
        self.request = request

    def _validate_token(self, token):
        settings = self.request.registry.settings
        signer = TimestampSigner(settings['payment.secret'])
        s = signer.unsign(token, max_age=86400)
        return int(s)

    def _make_method_profile(self, order, form):
        request = self.request
        ccf = form.data['cc']
        billing = model.Address(**ccf['billing'])

        gateway_id = request.registry.settings['payment_gateway_id']
        iface = payment.get_payment_interface(request.registry, gateway_id)

        try:
            profile = iface.create_profile(
                card_number=ccf['number'],
                exp_year=ccf['expires_year'],
                exp_month=ccf['expires_month'],
                ccv=ccf['code'],
                billing=billing,
                email=order.user.email,
            )
        except (socket.error, PaymentException) as e:
            if isinstance(e, socket.error):
                request.flash(
                    "A error occured while attempting to process the "
                    "transaction. Please try again.", 'error')
            else:
                request.flash(
                    "That credit card could not be processed. Please double "
                    "check that the information is correct.", 'error')
            return None, None

        method = model.PaymentMethod(
            user=order.user,
            payment_gateway_id=gateway_id,
            billing=billing,
            reference=profile.reference,
            save=ccf['save'] and (request.user == order.user),
            stripe_js=False,
            remote_addr=request.client_addr,
            user_agent=request.user_agent,
            session_id=request.session.id,
        )
        model.Session.add(method)

        return method, profile

    def _get_method_profile(self, order):
        request = self.request
        gateway_id = request.registry.settings['payment_gateway_id']
        iface = payment.get_payment_interface(request.registry, gateway_id)
        method = order.active_payment_method
        profile = iface.get_profile(method.reference)
        return method, profile

    @view_config(route_name='update-payment', renderer='update_payment.html')
    def index(self):
        request = self.request
        registry = request.registry

        order_id = self._validate_token(request.matchdict['token'])

        order = model.Order.get(order_id)

        # XXX handle this better, somehow
        assert order.current_due_amount > order.authorized_amount, \
            "this order doesn't need to update payment"

        try:
            masked_card = payment.get_masked_card(request.registry,
                                                  order.active_payment_method)
        except payment.UnknownGatewayException:
            if asbool(registry.settings.get('debug')):
                masked_card = 'XXXX????'
            else:
                raise

        form = Form(request, UpdatePaymentForm)
        if form.validate():
            if form.data['cc'] == 'saved':
                use_method, profile = self._get_method_profile(order)
            else:
                use_method, profile = self._make_method_profile(order, form)

            if use_method:
                amount = (order.current_due_amount - order.authorized_amount)
                descriptor = payment.make_descriptor(registry, order.id)

                # XXX Need error handling here!
                resp = profile.authorize(
                    amount=amount,
                    description='order-%d' % order.id,
                    statement_descriptor=descriptor,
                    ip=use_method.remote_addr,
                    user_agent=use_method.user_agent,
                    referrer=request.route_url('cart'),
                )

                order.active_payment_method = use_method
                order.payments.append(model.CreditCardPayment(
                    method=use_method,
                    transaction_id=resp['transaction_id'],
                    invoice_number=descriptor,
                    authorized_amount=amount,
                    amount=0,
                    avs_address1_result=resp['avs_address1_result'],
                    avs_zip_result=resp['avs_zip_result'],
                    ccv_result=resp['ccv_result'],
                    card_type=resp['card_type'],
                    created_by_id=request.user.id if request.user else 1,
                    descriptor=descriptor,
                ))

                request.flash("Thank you, your payment was successful. If "
                              "you would like to see the status of your "
                              "order(s), you may log in now.", 'success')
                return HTTPFound(location=request.route_url('account'))

        return {
            'order': order,
            'renderer': FormRenderer(form),
            'masked_card': masked_card,
        }
