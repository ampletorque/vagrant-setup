from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, validators

from ... import model, custom_validators

from ...editing import BaseEditView, BaseListView, BaseCreateView


@view_defaults(route_name='admin:vendor-order',
               renderer='admin/vendor_order.html')
@lift()
class VendorOrderEditView(BaseEditView):
    cls = model.VendorOrder

    class UpdateForm(Schema):
        "Schema for validating vendor order update form."
        loaded_time = validators.Number(not_empty=True)
        new_comment = custom_validators.CommentBody()


@view_defaults(route_name='admin:vendor-orders',
               renderer='admin/vendor_orders.html')
@lift()
class VendorOrderListView(BaseListView):
    cls = model.VendorOrder


@view_defaults(route_name='admin:vendor-orders:new',
               renderer='admin/vendor_orders_new.html')
@lift()
class VendorOrderCreateView(BaseCreateView):
    cls = model.VendorOrder
    obj_route_name = 'admin:vendor-order'

    class CreateForm(Schema):
        allow_extra_fields = False
        creator_id = validators.Int(not_empty=True)

    @view_config(permission='authenticated')
    def create(self):
        vars = BaseCreateView.create(self)
        vars['creators'] = \
            model.Session.query(model.Creator.id,
                                model.Creator.name).\
            order_by(model.Creator.name.desc())
        return vars
