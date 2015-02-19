from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, NestedVariables, validators

from pyramid_uniform import Form, FormRenderer

from ... import model, mail, custom_validators

from .base import BaseEditView, BaseListView


class EditAddressForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    shipping = custom_validators.AddressSchema


class EditUserForm(Schema):
    allow_extra_fields = False
    user_id = validators.Int(not_empty=True)


class AddPaymentForm(Schema):
    allow_extra_fields = False


class AddRefundForm(Schema):
    allow_extra_fields = False


class CancelForm(Schema):
    allow_extra_fields = False


@view_defaults(route_name='admin:order', renderer='admin/order.html')
@lift()
class OrderEditView(BaseEditView):
    cls = model.Order

    class UpdateForm(Schema):
        "Schema for validating order update form."
        pre_validators = [NestedVariables()]
        loaded_time = validators.Number(not_empty=True)
        new_comment = custom_validators.CommentBody()

    @view_config(route_name='admin:order:resend')
    def resend(self):
        request = self.request
        order = self._get_object()
        mail.send_order_confirmation(request, order)
        request.flash("Resent order confirmation to %s." % order.user.email,
                      'success')
        return HTTPFound(location=request.route_url('admin:order',
                                                    id=order.id))

    @view_config(route_name='admin:order:print',
                 renderer='paper/invoice.html')
    def print(self):
        order = self._get_object()
        assert order.unauthorized_amount == 0, \
            "cannot print an invoice for an unpaid order"
        # FIXME We want to be able to print partial invoices.
        items = order.cart.items
        return {'order': order, 'items': items}

    @view_config(route_name='admin:order:cancel',
                 renderer='admin/order_cancel.html')
    def cancel(self):
        request = self.request
        order = self._get_object()
        # XXX

        form = Form(request, schema=CancelForm)
        if form.validate():
            form.bind(order)
            request.flash("Order cancelled.", 'warning')
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:hold')
    def hold(self):
        request = self.request
        order = self._get_object()
        # XXX
        return HTTPFound(location=request.route_url('admin:order',
                                                    id=order.id))

    @view_config(route_name='admin:order:address',
                 renderer='admin/order_address.html')
    def address(self):
        request = self.request
        order = self._get_object()

        form = Form(request, schema=EditAddressForm)
        if form.validate():
            form.bind(order)
            request.flash("Updated address.", 'success')
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:user',
                 renderer='admin/order_user.html')
    def user(self):
        request = self.request
        order = self._get_object()

        form = Form(request, schema=EditUserForm)
        if form.validate():
            form.bind(order)
            request.flash("Updated user.", 'success')
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:payment',
                 renderer='admin/order_payment.html')
    def payment(self):
        request = self.request
        order = self._get_object()

        form = Form(request, schema=AddPaymentForm)
        if form.validate():
            # XXX do stuff
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:refund',
                 renderer='admin/order_refund.html')
    def refund(self):
        request = self.request
        order = self._get_object()

        form = Form(request, schema=AddRefundForm)
        if form.validate():
            # XXX do stuff
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}


@view_defaults(route_name='admin:orders', renderer='admin/orders.html')
@lift()
class OrderListView(BaseListView):
    cls = model.Order
    paginate = True
