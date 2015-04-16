from decimal import Decimal

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, ForEach, NestedVariables, validators

from pyramid_uniform import Form, FormRenderer

from ... import model, mail, custom_validators, payment, funds, helpers as h

from ...admin import BaseEditView, BaseListView, BaseCreateView


class EditAddressForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    shipping = custom_validators.AddressSchema


class EditUserForm(Schema):
    allow_extra_fields = False
    user_id = validators.Int(not_empty=True)


class AddNewCCPaymentForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    amount = custom_validators.Money(not_empty=True, min=0)
    cc = custom_validators.CreditCardSchema


class AddExistingCCPaymentForm(Schema):
    allow_extra_fields = False
    amount = custom_validators.Money(not_empty=True, min=0)
    method_id = validators.Int(not_empty=True)


class AddCashPaymentForm(Schema):
    allow_extra_fields = False
    amount = validators.Number(not_empty=True, min=0)


class AddCheckPaymentForm(Schema):
    allow_extra_fields = False
    amount = custom_validators.Money(not_empty=True, min=0)
    reference = validators.String(not_empty=True)
    check_date = validators.DateConverter(month_style='yyyy/mm/dd',
                                          not_empty=True)


class AddCashRefundForm(Schema):
    allow_extra_fields = False
    amount = custom_validators.Money(not_empty=True, min=0)


class AddCheckRefundForm(Schema):
    allow_extra_fields = False
    amount = custom_validators.Money(not_empty=True, min=0)
    reference = validators.Int(not_empty=True, min=0)


class CancelForm(Schema):
    allow_extra_fields = False
    reason = validators.String()
    item_ids = ForEach(validators.Int(not_empty=True))


class PrepareInvoiceForm(Schema):
    allow_extra_fields = False
    chained_validators = [custom_validators.ListNotEmpty('item_ids')]
    item_ids = ForEach(validators.Int(not_empty=True))


class FillForm(Schema):
    allow_extra_fields = False
    chained_validators = [custom_validators.ListNotEmpty('item_ids')]
    tracking_number = validators.String()
    shipped_by_creator = validators.Bool()
    cost = custom_validators.Money(not_empty=True, min=0)
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


class UpdateItemSchema(Schema):
    allow_extra_fields = False
    id = validators.Int(not_empty=True)
    price_each = custom_validators.Money(not_empty=True, min=Decimal('0.01'))
    shipping_price = custom_validators.Money(not_empty=True, min=0)
    qty_desired = validators.Int(not_empty=True, min=1)


@view_defaults(route_name='admin:order', renderer='admin/order.html',
               permission='admin')
@lift()
class OrderEditView(BaseEditView):
    cls = model.Order

    class UpdateForm(Schema):
        "Schema for validating order update form."
        pre_validators = [NestedVariables()]
        items = ForEach(UpdateItemSchema)
        new_comment = custom_validators.CommentBody()

    def _update_object(self, form, obj):
        for item_params in form.data.pop('items'):
            item = model.CartItem.get(item_params['id'])
            orig_qty_desired = item.qty_desired
            assert item.cart.order == obj
            item.qty_desired = item_params['qty_desired']
            item.price_each = item_params['price_each']
            item.shipping_price = item_params['shipping_price']
            # XXX This should probably be combined into one method call with
            # locking.
            if orig_qty_desired != item.qty_desired:
                item.release_stock()
                model.Session.flush()
                item.reserve_stock()
                model.Session.flush()
        BaseEditView._update_object(self, form, obj)

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

    @view_config(route_name='admin:order:send-update-payment')
    def send_update_payment(self):
        request = self.request
        order = self._get_object()
        self._touch_object(order)
        link = funds.update_payment_url(request, order)
        mail.send_update_payment_email(request, order, link)
        request.flash("Sent update payment email to %s." % order.user.email,
                      'success')
        return HTTPFound(location=request.route_url('admin:order',
                                                    id=order.id))

    @view_config(route_name='admin:order:prepare-invoice',
                 renderer='admin/order_prepare_invoice.html')
    def prepare_invoice(self):
        request = self.request
        order = self._get_object()
        self._touch_object(order)
        assert order.authorized_amount == order.current_due_amount, \
            "cannot print an invoice for an unpaid order"

        form = Form(request, PrepareInvoiceForm)
        if form.validate():
            for item_id in form.data['item_ids']:
                item = model.CartItem.get(item_id)
                assert item.cart.order == order
                item.status = 'being packed'
            return HTTPFound(
                location=request.route_url('admin:order:print-invoice',
                                           id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:print-invoice',
                 renderer='paper/invoice.html')
    def print_invoice(self):
        order = self._get_object()
        assert order.authorized_amount == order.current_due_amount, \
            "cannot print an invoice for an unpaid order"

        items_this_shipment = []
        items_other = []
        for item in order.cart.items:
            if item.status == 'being packed':
                items_this_shipment.append(item)
            elif not item.closed:
                items_other.append(item)

        assert len(items_this_shipment) > 0, "no items are being packed"

        return {
            'order': order,
            'items_this_shipment': items_this_shipment,
            'items_other': items_other,
        }

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

        if product.non_physical:
            item.refresh_non_physical()
        elif stage == model.CartItem.CROWDFUNDING:
            item.refresh_crowdfunding()
        elif stage == model.CartItem.PREORDER:
            item.refresh_preorder()
        elif stage == model.CartItem.STOCK:
            item.refresh_stock()
        else:
            raise Exception('unknown cart item state when adding')

        # XXX Need to set item status more correctly.
        item.status = 'payment pending'

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
            request.flash("Removed '%s' from order." % item.product.name,
                          'success')
            item.release_stock()
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

    @view_config(route_name='admin:order:payment-cash',
                 renderer='admin/order_payment_cash.html')
    def payment_cash(self):
        request = self.request
        order = self._get_object()
        form = Form(request, AddCashPaymentForm)
        if form.validate():
            order.payments.append(model.CashPayment(
                amount=form.data['amount'],
                created_by=request.user,
            ))
            request.flash("Added cash payment.", 'success')
            self._touch_object(order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {
            'obj': order,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:order:payment-check',
                 renderer='admin/order_payment_check.html')
    def payment_check(self):
        request = self.request
        order = self._get_object()
        form = Form(request, AddCheckPaymentForm)
        if form.validate():
            order.payments.append(model.CheckPayment(
                amount=form.data['amount'],
                reference=form.data['reference'],
                check_date=form.data['check_date'],
                created_by=request.user,
            ))
            request.flash("Added check payment.", 'success')
            self._touch_object(order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {
            'obj': order,
            'renderer': FormRenderer(form),
        }

    def _authorize_payment(self, order, method, amount):
        request = self.request
        registry = request.registry
        iface = payment.get_payment_interface(registry, method.gateway.id)
        descriptor = payment.make_descriptor(registry, order.id)
        profile = iface.get_profile(method.reference)
        resp = profile.authorize(
            amount=Decimal(amount),
            description='order-%d' % order.id,
            statement_descriptor=descriptor,
            ip=method.remote_addr,
            user_agent=method.user_agent,
            referrer=request.route_url('cart'),
        )
        order.payments.append(model.CreditCardPayment(
            method=method,
            transaction_id=resp['transaction_id'],
            invoice_number=descriptor,
            authorized_amount=amount,
            amount=0,
            avs_address1_result=resp['avs_address1_result'],
            avs_zip_result=resp['avs_zip_result'],
            ccv_result=resp['ccv_result'],
            card_type=resp['card_type'],
            created_by=request.user,
            descriptor=descriptor,
        ))

    @view_config(route_name='admin:order:payment-cc-existing',
                 renderer='admin/order_payment_cc_existing.html')
    def payment_cc_existing(self):
        request = self.request
        registry = request.registry
        order = self._get_object()

        masked_cards = {}

        def load(method):
            if method not in masked_cards:
                try:
                    masked_cards[method] = \
                        payment.get_masked_card(registry, method)
                except payment.UnknownGatewayException:
                    pass

        load(order.active_payment_method)

        saved_user_methods = []
        for method in order.user.payment_methods:
            saved_user_methods.append(method)
            load(method)

        saved_order_methods = []
        for pp in order.payments:
            if hasattr(pp, 'method'):
                if pp.method not in saved_order_methods:
                    saved_order_methods.append(pp.method)
                    load(pp.method)

        form = Form(request, AddExistingCCPaymentForm)
        if form.validate():
            method = model.PaymentMethod.get(form.data['method_id'])
            self._authorize_payment(order, method, form.data['amount'])
            self._touch_object(order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {
            'masked_cards': masked_cards,
            'saved_user_methods': saved_user_methods,
            'saved_order_methods': saved_order_methods,
            'obj': order,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:order:payment-cc-new',
                 renderer='admin/order_payment_cc_new.html')
    def payment_cc_new(self):
        request = self.request
        registry = request.registry
        order = self._get_object()

        form = Form(request, AddNewCCPaymentForm)
        if form.validate():
            ccf = form.data['cc']
            billing = model.Address(**ccf['billing'])
            gateway_id = registry.settings['payment_gateway_id']
            iface = payment.get_payment_interface(registry, gateway_id)
            profile = iface.create_profile(
                card_number=ccf['number'],
                exp_year=ccf['expires_year'],
                exp_month=ccf['expires_month'],
                ccv=ccf['code'],
                billing=billing,
                email=order.user.email,
            )
            method = model.PaymentMethod(
                user=order.user,
                payment_gateway_id=gateway_id,
                billing=billing,
                reference=profile.reference,
                save=False,
                stripe_js=False,
                remote_addr=request.client_addr,
                user_agent=request.user_agent,
                session_id=request.session.id,
            )
            model.Session.add(method)
            model.Session.flush()
            self._authorize_payment(order, method, form.data['amount'])
            self._touch_object(order)
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {
            'obj': order,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:order:refund-cash',
                 renderer='admin/order_refund_cash.html')
    def refund_cash(self):
        request = self.request
        order = self._get_object()

        form = Form(request, schema=AddCashRefundForm)
        if form.validate():
            amount = form.data['amount']
            refund = model.CashRefund(
                refund_amount=-amount,
                amount=-amount,
                created_by=request.user,
            )
            order.payments.append(refund)
            self._touch_object(order)
            request.flash("Added cash refund of %s." % h.currency(amount),
                          'success')
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=order.id))

        return {'obj': order, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:order:refund-check',
                 renderer='admin/order_refund_check.html')
    def refund_check(self):
        request = self.request
        order = self._get_object()

        form = Form(request, schema=AddCheckRefundForm)
        if form.validate():
            amount = form.data['amount']
            refund = model.CheckRefund(
                refund_amount=-amount,
                amount=-amount,
                reference=form.data['reference'],
                created_by=request.user,
            )
            order.payments.append(refund)
            self._touch_object(order)
            request.flash("Added check refund of %s." % h.currency(amount),
                          'success')
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
        user_id = validators.Int(not_empty=True)

    def _create_object(self, form):
        cart = model.Cart()
        obj = self.cls(cart=cart, **form.data)
        model.Session.add(obj)
        return obj
