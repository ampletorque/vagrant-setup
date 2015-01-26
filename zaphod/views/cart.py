from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.view import view_config

from formencode import Schema, ForEach, NestedVariables, validators
from pyramid_uniform import Form, FormRenderer

from .. import model


class CheckoutForm(Schema):
    "Validates checkout submissions."
    allow_extra_fields = False
    # XXX add everything


class AddToCartSchema(Schema):
    "Validates add-to-cart actions."
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    product_id = validators.Int(not_empty=True)
    qty = validators.Int(not_empty=True, min=1)
    options = ForEach(validators.Int(not_empty=True))


class CartView(object):
    def __init__(self, request):
        self.request = request

    def get_cart(self, create_new=False):
        request = self.request
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = model.Cart.get(cart_id)
        elif create_new:
            cart = model.Cart()
            model.Session.add(cart)
        else:
            cart = None
        return cart

    @view_config(route_name='cart', renderer='cart.html')
    def cart(self):
        request = self.request
        cart = self.get_cart()

        form = Form(request, schema=CheckoutForm)
        if form.validate():
            # XXX process order

            return HTTPFound(location=request.route_url('cart:confirmed'))

        return dict(cart=cart, renderer=FormRenderer(form))

    @view_config(route_name='cart:add')
    def add(self):
        request = self.request
        cart = self.get_cart()

        form = Form(request, schema=AddToCartSchema)
        if form.validate():
            product = model.Product.get(form.data['product_id'])
            if not product:
                raise HTTPBadRequest
            ci = model.CartItem(
                qty_desired=form.data['qty'],
                product=product,
                cart=cart,
                # XXX Lots of other columns to add here.
            )
            for opt_id in form.data['options']:
                ov = model.OptionValue.get(opt_id)
                ci.option_values.add(ov)
            ci.price_each = ci.calculate_price()
            model.Session.add(ci)

            return HTTPFound(location=request.route_url('cart'))
        else:
            raise HTTPBadRequest

    @view_config(route_name='cart:confirmed', renderer='order.html')
    def confirmed(self):
        request = self.request
        order_id = request.session.get('order_id')
        if order_id:
            order = model.Order.get(order_id)
        else:
            raise HTTPBadRequest
        return dict(order=order)
