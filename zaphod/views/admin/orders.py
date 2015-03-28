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
    chained_validators = [custom_validators.ListNotEmpty('item_ids')]
    tracking_number = validators.UnicodeString()
    shipped_by_creator = validators.Bool()
    cost = validators.Number(not_empty=True)
    item_ids = ForEach(validators.Int(not_empty=True))
    send_tracking_email = validators.Bool()


class AddItemForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    product_id = validators.Int(not_empty=True)
    options = ForEach(validators.Int(not_empty=True))
    qty = validators.Int(not_empty=True, min=1, max=99)
    stage = validators.OneOf(['crowdfunding', 'pre-order', 'stock'],
                             not_empty=True)


class RemoveItemForm(Schema):
    allow_extra_fields = False


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
            order.ship_items(
                items=items,
                tracking_number=form.data['tracking_number'],
                cost=form.data['cost'],
                shipped_by_creator=form.data['shipped_by_creator'],
                user=request.user)
            s = 'Order filled. '
            if form.data['send_tracking_email']:
                mail.send_shipping_confirmation(request, order)
                s += 'Shipping confirmation email sent.'
            else:
                s += 'Shipping confirmation email not sent.'
            request.flash(s, 'success')
            self._touch_object(order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))
        return {'obj': order, 'renderer': FormRenderer(form)}

    def _process_add_item(self, form, order):
        request = self.request
        product = model.Product.get(form.data['product_id'])
        stage = {
            'crowdfunding': model.CartItem.CROWDFUNDING,
            'pre-order': model.CartItem.PREORDER,
            'stock': model.CartItem.STOCK,
        }[form.data['stage']]

        sku = model.sku_for_option_value_ids(product, form.data['options'])
        item = model.CartItem(
            cart=order.cart,
            stage=stage,
            product=product,
            sku=sku,
            qty_desired=form.data['qty'],
            shipping_price=0,
            price_each=product.price,
        )
        model.Session.add(item)
        # XXX need to figure out how to update status and allocate stock here,
        # but item.refresh() can't do it because that will update the stage

        request.flash("Added '%s' to order." % product.name, 'success')
        self._touch_object(order)

    @view_config(route_name='admin:order:add-item',
                 renderer='admin/order_add_item.html')
    def add_item(self):
        request = self.request
        order = self._get_object()
        form = Form(request, AddItemForm)
        if form.validate():
            self._process_add_item(form, order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:add-item', request_method='POST',
                 xhr=True, renderer='json')
    def add_item_ajax(self):
        request = self.request
        order = self._get_object()
        form = Form(request, AddItemForm)
        if form.validate():
            self._process_add_item(form, order)
            return {
                'status': 'ok',
                'location': request.route_url('admin:order', id=order.id),
            }
        else:
            return {
                'status': 'fail',
                'errors': form.errors,
            }

    @view_config(route_name='admin:order:remove-item',
                 renderer='admin/order_remove_item.html')
    def remove_item(self):
        request = self.request
        order = self._get_object()
        item = model.CartItem.get(request.matchdict['item_id'])
        form = Form(request, RemoveItemForm)
        assert item.cart.order == order
        if form.validate():
            request.flash("Removed '%s' to order." % item.product.name,
                          'success')
            model.Session.delete(item)
            self._touch_object(order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {
            'obj': order,
            'item': item,
            'renderer': FormRenderer(form)
        }

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

        saved_methods = []
        # gather payment methods from user and from this order
        for method in order.user.payment_methods:
            if method not in saved_methods:
                saved_methods.append(method)
        for payment in order.payments:
            if hasattr(payment, 'method'):
                if payment.method not in saved_methods:
                    saved_methods.append(payment.method)

        form = Form(request, AddPaymentForm)
        if form.validate():
            # XXX do stuff
            self._touch_object(order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {
            'saved_methods': saved_methods,
            'obj': order,
            'renderer': FormRenderer(form),
        }

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
