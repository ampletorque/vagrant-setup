from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.view import view_config

from formencode import Schema, ForEach, NestedVariables, validators
from pyramid_uniform import Form, FormRenderer

from .. import model, custom_validators


class CheckoutForm(Schema):
    "Validates checkout submissions."
    allow_extra_fields = False
    pre_validators = [NestedVariables]

    shipping = custom_validators.AddressSchema

    save_credit_card = validators.Bool()
    billing_same_as_shipping = validators.Bool()
    billing = custom_validators.AddressSchema

    email = validators.Email(not_empty=True)
    comments = validators.UnicodeString()

    cc = custom_validators.SelectValidator(
        {'empty': custom_validators.WildcardSchema()},
        default=custom_validators.CreditCardSchema(),
        selector_field='method')


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

    @view_config(route_name='cart', renderer='cart.html')
    def cart(self):
        request = self.request
        cart = self.get_cart()

        cart.refresh()

        form = Form(request, schema=CheckoutForm)
        if form.validate():
            # XXX process order

            return HTTPFound(location=request.route_url('cart:confirmed'))

        return dict(cart=cart, renderer=FormRenderer(form))

    @view_config(route_name='cart:add')
    def add(self):
        request = self.request

        form = Form(request, schema=CartItemAddSchema)
        if form.validate():
            product = model.Product.get(form.data['product_id'])
            if not product:
                raise HTTPBadRequest

            cart = self.get_cart(create_new=True)

            project = product.project
            crowdfunding = project.status == 'crowdfunding'
            batch = product.current_batch

            # ov_ids = set(model.OptionValue.get(ov_id) for ov_id in
            #              form.data['options'])
            # XXX Select or generate SKU based on option values

            assert cart and cart.id
            ci = model.CartItem(
                cart=cart,
                qty_desired=form.data['qty'],
                product=product,
                shipping_price=0,
                crowdfunding=crowdfunding,
                batch=batch,
                expected_delivery_date=batch.delivery_date,
                status='cart',
            )
            ci.price_each = ci.calculate_price()
            model.Session.add(ci)

            request.flash("Added '%s' to your shopping cart." % product.name,
                          'success')
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
            assert ci.cart == cart
            name = ci.product.name
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
                    model.Session.delete(ci)

            request.flash("Updated item quantities.", 'success')
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
