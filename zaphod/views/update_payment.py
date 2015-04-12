from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid_uniform import Form, FormRenderer
from formencode import Schema, NestedVariables, validators
from itsdangerous import TimestampSigner

from .. import model, payment, custom_validators


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

    @view_config(route_name='update-payment', renderer='update_payment.html')
    def index(self):
        request = self.request

        # XXX Remove this once ready for prod
        assert request.registry.settings['debug'] == 'true'

        order_id = self._validate_token(request.matchdict['token'])

        order = model.Order.get(order_id)

        try:
            masked_card = payment.get_masked_card(request.registry,
                                                  order.active_payment_method)
        except payment.UnknownGatewayException:
            masked_card = 'XXXX1234'

        form = Form(request, UpdatePaymentForm)
        if form.validate():
            # XXX Try to process payment.

            success = False
            if success:
                # XXX Update payment status, etc.

                request.flash("Successfully processed transaction.")
                return HTTPFound(location=request.route_url('account'))
            else:
                request.flash("The transaction could not be processed.",
                              'error')

        return {
            'order': order,
            'renderer': FormRenderer(form),
            'masked_card': masked_card,
        }
