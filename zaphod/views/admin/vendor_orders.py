from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, validators

from ... import model

from .base import BaseEditView, BaseListView


@view_defaults(route_name='admin:vendor_order',
               renderer='admin/vendor_order.html')
@lift()
class VendorOrderEditView(BaseEditView):
    cls = model.VendorOrder

    class UpdateForm(Schema):
        "Schema for validating vendor order update form."
        loaded_time = validators.Number(not_empty=True)


@view_defaults(route_name='admin:vendor_orders',
               renderer='admin/vendor_orders.html')
@lift()
class VendorOrderListView(BaseListView):
    cls = model.VendorOrder
