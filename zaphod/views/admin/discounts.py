from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, validators

from ... import model, custom_validators

from ...admin import BaseEditView, BaseListView, BaseCreateView


@view_defaults(route_name='admin:discount',
               renderer='admin/discount.html', permission='admin')
@lift()
class DiscountEditView(BaseEditView):
    cls = model.Discount

    class UpdateForm(Schema):
        allow_extra_fields = False
        description = validators.UnicodeString(not_empty=True, strip=True)
        rate = validators.Number(not_empty=True)
        published = validators.Bool()
        enabled = validators.Bool()


@view_defaults(route_name='admin:discounts',
               renderer='admin/discounts.html', permission='admin')
@lift()
class DiscountListView(BaseListView):
    cls = model.Discount


@view_defaults(route_name='admin:discounts:new',
               renderer='admin/discounts_new.html', permission='admin')
@lift()
class DiscountCreateView(BaseCreateView):
    cls = model.Discount
    obj_route_name = 'admin:discount'

    class CreateForm(Schema):
        allow_extra_fields = False
        creator_id = validators.Int(not_empty=True)
        description = validators.UnicodeString(not_empty=True)
