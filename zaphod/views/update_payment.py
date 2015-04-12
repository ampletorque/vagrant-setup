from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPBadRequest
from pyramid_uniform import Form, FormRenderer
from formencode import Schema, NestedVariables, validators

from .. import model, funds


class UpdatePaymentParams(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    order_id = validators.Int(not_empty=True)
    timestamp = validators.Int(not_empty=True)
    sig = validators.String()


class UpdatePaymentForm(UpdatePaymentParams):
    pass


class UpdatePaymentView(object):
    def __init__(self, request):
        self.request = request

    def _validate_sig(self, params):
        if not funds.verify_update_token(params.data['sig'],
                                         params.data['order_id'],
                                         params.data['timestamp']):
            raise HTTPForbidden

    @view_config(route_name='update-payment', renderer='update_payment.html')
    def index(self):
        request = self.request

        # XXX
        assert request.registry.settings['debug'] == 'true'

        params = Form(request, UpdatePaymentParams, method=request.method)
        if not params.validate(skip_csrf=True):
            raise HTTPBadRequest

        self._validate_sig(params)

        order = model.Order.get(params.data['order_id'])

        # XXX fill this in for real
        masked_card = 'XXXX1234'

        form = Form(request, UpdatePaymentForm)
        if form.validate():
            # XXX Try to process payment.

            request.flash("Successfully processed transaction.")
            return HTTPFound(location=request.route_url('account'))

        return {
            'order': order,
            'renderer': FormRenderer(form),
            'masked_card': masked_card,
        }
