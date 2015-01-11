from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.view import view_config

from formencode import Schema, validators
from pyramid_uniform import Form, FormRenderer

from .. import model


class CheckoutForm(Schema):
    "Validates checkout submissions."
    allow_extra_fields = False
    # XXX add everything


class AddToCartSchema(Schema):
    "Validates add-to-cart actions."
    allow_extra_fields = False
    pledge_level_id = validators.Int(not_empty=True)
    qty = validators.Int(not_empty=True, min=1)
    # XXX add options


class CartView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='cart', renderer='cart.html')
    def cart(self):
        request = self.request
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = model.Cart.get(cart_id)
        else:
            cart = None

        form = Form(request, schema=CheckoutForm)
        if form.validate():
            # XXX process order

            return HTTPFound(location=request.route_url('cart:confirmed'))

        return dict(cart=cart, renderer=FormRenderer(form))

    @view_config(route_name='cart:add')
    def add(self):
        request = self.request

        form = Form(request, schema=AddToCartSchema)
        if form.validate():
            # XXX add items to cart

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
