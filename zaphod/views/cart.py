from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import socket

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.view import view_config

from formencode import Schema, ForEach, NestedVariables, validators
from pyramid_uniform import Form, FormRenderer
from pyramid_es import get_client

from .. import model, mail, custom_validators, payment
from ..payment.exc import PaymentException

log = logging.getLogger(__name__)


class CheckoutForm(Schema):
    "Validates checkout submissions."
    allow_extra_fields = False
    pre_validators = [
        NestedVariables,
        custom_validators.CloneFields(
            'shipping', 'cc.billing',
            when='billing_same_as_shipping'),
        custom_validators.CloneFields(
            'cc.billing', 'shipping',
            when='non_physical')]

    shipping = custom_validators.AddressSchema

    billing_same_as_shipping = validators.Bool()
    non_physical = validators.Bool()

    email = validators.Email(not_empty=True, strip=True)
    comments = validators.UnicodeString()

    cc = custom_validators.SelectValidator(
        {'yes': validators.Constant('saved')},
        default=custom_validators.CreditCardSchema(),
        selector_field='use_saved')


class CartItemAddSchema(Schema):
    "Validates add-to-cart actions."
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    product_id = validators.Int(not_empty=True)
    qty = validators.Int(not_empty=True, min=1, max=99)
    options = ForEach(validators.Int(not_empty=True))


class CartItemRemoveSchema(Schema):
    "Validates remove-from-cart actions."
    allow_extra_fields = False
    id = validators.Int(not_empty=True)


class CartItemUpdateSchema(Schema):
    allow_extra_fields = False
    id = validators.Int(not_empty=True)
    qty = validators.Int(not_empty=True, min=0, max=99)


class CartUpdateSchema(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    items = ForEach(CartItemUpdateSchema)


class CartView(object):
    def __init__(self, request):
        self.request = request

    def get_cart(self, create_new=False):
        request = self.request
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = model.Session.query(model.Cart).\
                filter(model.Cart.id == cart_id).\
                filter(model.Cart.order == None).\
                first()
            if cart:
                return cart
            else:
                request.session['cart_id'] = None

        if create_new:
            cart = model.Cart()
            model.Session.add(cart)
            model.Session.flush()
            request.session['cart_id'] = cart.id
            return cart

    @view_config(route_name='cart:add')
    def add(self):
        request = self.request

        form = Form(request, schema=CartItemAddSchema, skip_csrf=True)
        if form.validate():
            product = model.Product.get(form.data['product_id'])
            cart = self.get_cart(create_new=True)
            if not (product and cart and cart.id):
                raise HTTPBadRequest

            sku = model.sku_for_option_value_ids(product, form.data['options'])
            ci = model.Session.query(model.CartItem).\
                filter_by(cart=cart, sku=sku).first()

            if ci:
                ci.qty_desired += 1
                request.flash("'%s' was already in your cart, so "
                              "the qty has been increased to %d." %
                              (product.name, ci.qty_desired), 'success')
            else:
                ci = model.CartItem(
                    cart=cart,
                    qty_desired=form.data['qty'],
                    product=product,
                    shipping_price=0,
                    sku=sku,
                    stage=0,
                    price_each=0
                )
                ci.refresh()
                request.flash("Added '%s' to your shopping cart." %
                              product.name, 'success')
            return HTTPFound(location=request.route_url('cart'))
        else:
            raise HTTPBadRequest

    @view_config(route_name='cart:remove')
    def remove(self):
        request = self.request

        form = Form(request, schema=CartItemRemoveSchema, method='GET')
        if form.validate():
            cart = self.get_cart(create_new=True)
            ci = model.CartItem.get(form.data['id'])
            if ci:
                assert ci.cart == cart
                name = ci.product.name
                ci.release_stock()
                model.Session.delete(ci)
                request.flash("Removed '%s' from your shopping cart." % name,
                              'info')
            return HTTPFound(location=request.route_url('cart'))
        else:
            raise HTTPBadRequest

    @view_config(route_name='cart:update')
    def update(self):
        request = self.request

        form = Form(request, schema=CartUpdateSchema)
        if form.validate():
            cart = self.get_cart(create_new=True)

            for item_params in form.data['items']:
                ci = model.CartItem.get(item_params['id'])
                assert ci.cart == cart
                ci.qty_desired = item_params['qty']
                if ci.qty_desired == 0:
                    ci.release_stock()
                    model.Session.delete(ci)

            request.flash("Updated item quantities.", 'success')
            return HTTPFound(location=request.route_url('cart'))
        else:
            raise HTTPBadRequest

    def _get_or_create_user(self, email, shipping):
        request = self.request
        user = model.Session.query(model.User).\
            filter_by(email=email).\
            first()

        if not user:
            if shipping.country_code == 'us':
                location = '%s, %s' % (shipping.city,
                                       shipping.state)
            else:
                location = '%s, %s' % (shipping.city,
                                       shipping.country_name)
            user = model.User(
                name=shipping.full_name,
                email=email,
                show_location=location,
                show_name='%s %s' % (shipping.first_name,
                                     shipping.last_name[0]))
            model.Session.add(user)
            token = user.set_reset_password_token()
            mail.send_welcome_email(request, user, token)
            client = get_client(request)
            client.index_object(user)

        return user

    def _handle_new_payment(self, order, form, email, user):
        request = self.request
        session = request.session
        cart = order.cart

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
                email=email,
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

            log.info('payment_failed order:%d cart:%s', order.id, cart.id)

            mail.send_with_admin(request,
                                 'checkout_failure',
                                 vars=dict(
                                     billing=billing,
                                     customer_email=email,
                                     session_id=session.id,
                                     order=order,
                                     exc=e,
                                 ),
                                 to=[request.registry.settings['mailer.from']],
                                 immediately=True)

            raise HTTPFound(location=request.route_url('cart'))

        method = model.PaymentMethod(
            user=user,
            payment_gateway_id=gateway_id,
            billing=billing,
            reference=profile.reference,
            save=ccf['save'],
            stripe_js=False,
            remote_addr=request.client_addr,
            user_agent=request.user_agent,
            session_id=request.session.id,
        )
        model.Session.add(method)

        order.active_payment_method = method

    def _place_order(self, cart, form, payment_method):
        request = self.request

        email = form.data['email']
        shipping = model.Address(**form.data['shipping'])
        comments = form.data['comments']

        # update item shipping prices in case of international
        if shipping.country_code != 'us':
            cart.set_international_shipping()

        # update item statuses
        cart.set_initial_statuses()

        # fetch or create user
        user = self._get_or_create_user(email, shipping)

        # get ids to invalidate
        project_ids = set(ci.product.project_id for ci in cart.items)

        order = model.Order(
            user=user,
            cart=cart,
            customer_comments=comments,
            shipping=shipping,
        )
        model.Session.add(order)
        model.Session.flush()

        if form.data['cc'] == 'saved':
            order.active_payment_method = payment_method
        else:
            self._handle_new_payment(order, form, email, user)

        # Save the order ID
        request.session['new_order_id'] = order.id

        mail.send_order_confirmation(request, order)

        request.flash('Order confirmed!', 'success')

        client = get_client(request)
        client.index_object(order)

        # invalidate redis cache
        request.theme.invalidate_index()
        for project_id in project_ids:
            request.theme.invalidate_project(project_id)

    @view_config(route_name='cart', renderer='cart.html')
    def cart(self):
        request = self.request
        registry = request.registry
        cart = self.get_cart()

        if cart:
            cart.refresh()
            for ci in cart.items:
                if not ci.qty_desired:
                    request.flash("'%s' is not available, it has "
                                  "been removed from your cart." %
                                  ci.product.name, 'warning')
                    cart.items.remove(ci)
            model.Session.flush()

        billing = shipping = masked_card = payment_method = None

        if cart and request.user:
            last_order = model.Session.query(model.Order).\
                filter_by(user=request.user).\
                order_by(model.Order.id.desc()).\
                first()

            if last_order:
                shipping = last_order.shipping

            payment_method = model.Session.query(model.PaymentMethod).\
                filter_by(save=True, user=request.user).\
                order_by(model.PaymentMethod.id.desc()).\
                first()

            if payment_method:
                try:
                    masked_card = \
                        payment.get_masked_card(registry, payment_method)
                    billing = payment_method.billing
                except payment.UnknownGatewayException:
                    pass

        form = Form(request, schema=CheckoutForm)
        if cart and form.validate():
            self._place_order(cart, form, payment_method)
            return HTTPFound(location=request.route_url('cart:confirmed'))

        return {
            'cart': cart,
            'renderer': FormRenderer(form),
            'shipping': shipping,
            'billing': billing,
            'masked_card': masked_card,
        }

    @view_config(route_name='cart:confirmed', renderer='order.html')
    def confirmed(self):
        request = self.request
        order_id = request.session.get('new_order_id')
        if order_id:
            order = model.Order.get(order_id)
            del request.session['new_order_id']
        else:
            raise HTTPBadRequest
        return {
            'order': order,
            'first_load': True,
        }
