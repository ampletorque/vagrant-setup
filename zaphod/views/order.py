from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config, view_defaults
from formencode import Schema, NestedVariables
from pyramid_uniform import Form, FormRenderer

from .. import model, mail, custom_validators


class UpdateOrderForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    shipping = custom_validators.AddressSchema


@view_defaults(permission='authenticated')
class OrderView(object):
    def __init__(self, request):
        self.request = request

    def _get_order(self):
        request = self.request
        order_id = request.matchdict['id']
        try:
            return model.Session.query(model.Order).\
                filter_by(user=request.user, id=order_id).\
                one()
        except NoResultFound:
            raise HTTPNotFound

    @view_config(route_name='order', renderer='order.html')
    def order(self):
        order = self._get_order()
        return {'order': order, 'first_load': False}

    @view_config(route_name='order:update', renderer='order_update.html')
    def order_update(self):
        request = self.request
        order = self._get_order()

        assert not order.closed, \
            "attempted to view order update page for closed order"

        form = Form(request, UpdateOrderForm)
        if form.validate():
            new_address = model.Address(**form.data['shipping'])

            vars = {
                'order': order,
                'new_address': new_address,
            }

            mail.send_with_admin(request, 'order_update', vars,
                                 to=[request.registry.settings['mailer.from']],
                                 reply_to=order.user.email)

            request.flash("Our support staff has been notified of your "
                          "desired address change. You will receive a "
                          "confirmation when this order has been updated.",
                          'success')
            return HTTPFound(location=request.route_url('order', id=order.id))

        return {'order': order, 'renderer': FormRenderer(form)}
