from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, NestedVariables, validators

from ... import model, mail

from .base import BaseEditView, BaseListView


@view_defaults(route_name='admin:order', renderer='admin/order.html')
@lift()
class OrderEditView(BaseEditView):
    cls = model.Order

    class UpdateForm(Schema):
        "Schema for validating order update form."
        pre_validators = [NestedVariables()]
        loaded_time = validators.Number(not_empty=True)

    @view_config(route_name='admin:order-resend')
    def resend(self):
        request = self.request
        order_id = request.matchdict['id']
        order = model.Order.get(order_id)
        mail.send_order_confirmation(request, order)
        request.flash("Resent order confirmation to %s." % order.user.email,
                      'success')
        return HTTPFound(location=request.route_url('admin:order',
                                                    id=order.id))


@view_defaults(route_name='admin:orders', renderer='admin/orders.html')
@lift()
class OrderListView(BaseListView):
    cls = model.Order
