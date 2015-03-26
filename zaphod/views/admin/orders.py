from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, ForEach, NestedVariables, validators

from pyramid_uniform import Form, FormRenderer

from ... import model, mail, custom_validators

from ...admin import BaseEditView, BaseListView, BaseCreateView


class EditAddressForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    shipping = custom_validators.AddressSchema


class EditUserForm(Schema):
    allow_extra_fields = False
    user_id = validators.Int(not_empty=True)


class AddPaymentForm(Schema):
    allow_extra_fields = False
    # XXX


class AddRefundForm(Schema):
    allow_extra_fields = False
    # XXX


class CancelForm(Schema):
    allow_extra_fields = False
    reason = validators.UnicodeString()
    item_ids = ForEach(validators.Int(not_empty=True))


class FillForm(Schema):
    allow_extra_fields = False
    tracking_number = validators.UnicodeString()
    shipped_by_creator = validators.Bool()
    cost = validators.Number()
    item_ids = ForEach(validators.Int(not_empty=True))


class AddItemForm(Schema):
    allow_extra_fields = False
    # XXX


@view_defaults(route_name='admin:order', renderer='admin/order.html',
               permission='admin')
@lift()
class OrderEditView(BaseEditView):
    cls = model.Order

    class UpdateForm(Schema):
        "Schema for validating order update form."
        pre_validators = [NestedVariables()]
        loaded_time = validators.Number(not_empty=True)
        new_comment = custom_validators.CommentBody()

    @view_config(route_name='admin:order:resend-confirmation')
    def resend_confirmation(self):
        request = self.request
        order = self._get_object()
        self._touch_object(order)
        mail.send_order_confirmation(request, order)
        request.flash("Resent order confirmation to %s." % order.user.email,
                      'success')
        return HTTPFound(location=request.route_url('admin:order',
                                                    id=order.id))

    @view_config(route_name='admin:order:resend-shipping-confirmation')
    def resend_shipping_confirmation(self):
        request = self.request
        order = self._get_object()
        self._touch_object(order)
        mail.send_shipping_confirmation(request, order)
        request.flash("Resent shipping confirmation to %s." % order.user.email,
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
        form = Form(request, CancelForm)
        if form.validate():
            items = set()
            for item_id in form.data['item_ids']:
                ci = model.CartItem.get(item_id)
                assert ci.cart.order == order
                items.add(ci)
            if items:
                order.cancel(items=items,
                             reason=form.data['reason'],
                             user=request.user)
                request.flash("Order cancelled.", 'warning')
                self._touch_object(order)
                return HTTPFound(location=request.route_url('admin:order',
                                                            id=order.id))
            else:
                request.flash("No items were selected.", 'error')

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:fill',
                 renderer='admin/order_fill.html')
    def fill(self):
        request = self.request
        order = self._get_object()
        form = Form(request, FillForm)
        if form.validate():
            items = set()
            for item_id in form.data['item_ids']:
                ci = model.CartItem.get(item_id)
                assert ci.cart.order == order
                items.add(ci)
            if items:
                order.ship_items(
                    items=items,
                    tracking_number=form.data['tracking_number'],
                    cost=form.data['cost'],
                    shipped_by_creator=form.data['shipped_by_creator'],
                    user=request.user)
                request.flash("Order updated.", 'success')
                self._touch_object(order)
                return HTTPFound(location=request.route_url('admin:order',
                                                            id=order.id))
            else:
                request.flash("No items were selected.", 'error')

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:add-item',
                 renderer='admin/order_add_item.html')
    def add_item(self):
        request = self.request
        order = self._get_object()
        form = Form(request, schema=AddItemForm)
        if form.validate():
            product = model.Product.get(form.data['product_id'])
            # XXX

            request.flash("Added '%s' to order." % product.name, 'success')
            self._touch_object(order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:address',
                 renderer='admin/order_address.html')
    def address(self):
        request = self.request
        order = self._get_object()

        form = Form(request, schema=EditAddressForm)
        if form.validate():
            form.bind(order)
            request.flash("Updated address.", 'success')
            self._touch_object(order)
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
            self._touch_object(order)
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
            self._touch_object(order)
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
            self._touch_object(order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}


@view_defaults(route_name='admin:orders', renderer='admin/orders.html',
               permission='admin')
@lift()
class OrderListView(BaseListView):
    cls = model.Order
    paginate = True

    @view_config(route_name='admin:orders',
                 renderer='admin/orders.html')
    def index(self):
        vars = BaseListView.index(self)
        q = model.Session.query(model.Order).filter_by(closed=False)
        vars['num_open'] = q.count()
        return vars


@view_defaults(route_name='admin:orders:new',
               renderer='admin/orders_new.html', permission='admin')
@lift()
class OrderCreateView(BaseCreateView):
    cls = model.Order
    obj_route_name = 'admin:order'

    class CreateForm(Schema):
        allow_extra_fields = False
        pre_validators = [NestedVariables()]
        # XXX add lots here
