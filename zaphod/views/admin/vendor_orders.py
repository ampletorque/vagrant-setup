from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from formencode import Schema, NestedVariables, validators

from pyramid_uniform import Form, FormRenderer

from ... import model


class UpdateForm(Schema):
    "Schema for validating vendor order update form."
    pre_validators = [NestedVariables()]
    loaded_time = validators.Number(not_empty=True)


class OrdersView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:vendor_orders',
                 renderer='admin/vendor_orders.html',
                 permission='authenticated')
    def index(self):
        q = model.Session.query(model.VendorOrder).limit(100)
        return dict(vendor_orders=q.all())

    @view_config(route_name='admin:vendor_order',
                 renderer='admin/vendor_order.html',
                 permission='authenticated')
    def edit(self):
        request = self.request
        vendor_order = model.VendorOrder.get(request.matchdict['id'])

        form = Form(request, schema=UpdateForm)
        if form.validate():
            # XXX do shit
            pass

        return dict(vendor_order=vendor_order, renderer=FormRenderer(form))
