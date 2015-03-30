from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPBadRequest
from pyramid_uniform import Form
from formencode import Schema, NestedVariables, validators

from .. import model, funds


class UpdatePaymentParams(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    order_id = validators.Int(not_empty=True)
    project_id = validators.Int(not_empty=True)
    timestamp = validators.Int(not_empty=True)
    sig = validators.String()


class UpdatePaymentView(object):
    def __init__(self, request):
        self.request = request

    def _validate_sig(self, params):
        if not funds.verify_update_token(params.data['sig'],
                                         params.data['order_id'],
                                         params.data['project_id'],
                                         params.data['timestamp']):
            raise HTTPForbidden

    @view_config(route_name='update-payment', renderer='update_payment.html')
    def index(self):
        request = self.request

        params = Form(request, UpdatePaymentParams, method=request.method)
        if not params.validate(skip_csrf=True):
            raise HTTPBadRequest

        self._validate_sig(params)

        order = model.Order.get(params.data['order_id'])
        project = model.Project.get(params.data['project_id'])

        return {
            'order': order,
            'project': project,
        }
