from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, NestedVariables, validators

from ... import model

from .base import BaseEditView, BaseListView


class UpdateForm(Schema):
    "Schema for validating order update form."
    pre_validators = [NestedVariables()]
    loaded_time = validators.Number(not_empty=True)


@view_defaults(route_name='admin:order', renderer='admin/order.html')
@lift()
class OrderEditView(BaseEditView):
    cls = model.Order


@view_defaults(route_name='admin:orders', renderer='admin/orders.html')
@lift()
class OrderListView(BaseListView):
    cls = model.Order
