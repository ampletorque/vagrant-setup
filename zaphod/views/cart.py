from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.view import view_config

from formencode import Schema, ForEach, NestedVariables, validators
from pyramid_uniform import Form, FormRenderer

from .. import model, custom_validators, payment


class CheckoutForm(Schema):
    "Validates checkout submissions."
    allow_extra_fields = False
    pre_validators = [NestedVariables,
                      custom_validators.CloneFields(
                          'shipping', 'billing',
                          when='billing_same_as_shipping')]

    shipping = custom_validators.AddressSchema

    billing_same_as_shipping = validators.Bool()
    billing = custom_validators.AddressSchema

    email = validators.Email(not_empty=True)
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

        form = Form(request, schema=CartItemAddSchema)
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

    @view_config(route_name='cart', renderer='cart.html')
    def cart(self):
        request = self.request
        registry = request.registry
        cart = self.get_cart()

        if cart:
            cart.refresh()

        billing = shipping = masked_card = None

        if cart and request.user:
            email = request.user.email

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
        if form.validate():
            # XXX process order
            assert False

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
        order_id = request.session.get('order_id')
        if order_id:
            order = model.Order.get(order_id)
        else:
            raise HTTPBadRequest
        return dict(order=order)
