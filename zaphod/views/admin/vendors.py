from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, validators

from ... import model, custom_validators

from ...admin import BaseEditView, BaseListView, BaseCreateView


@view_defaults(route_name='admin:vendor',
               renderer='admin/vendor.html')
@lift()
class VendorEditView(BaseEditView):
    cls = model.Vendor

    class UpdateForm(Schema):
        loaded_time = validators.Number(not_empty=True)
        new_comment = custom_validators.CommentBody()


@view_defaults(route_name='admin:vendors',
               renderer='admin/vendors.html')
@lift()
class VendorListView(BaseListView):
    cls = model.Vendor


@view_defaults(route_name='admin:vendors:new',
               renderer='admin/vendors_new.html')
@lift()
class VendorCreateView(BaseCreateView):
    cls = model.Vendor
    obj_route_name = 'admin:vendor'

    class CreateForm(Schema):
        allow_extra_fields = False
        name = validators.UnicodeString(not_empty=True)
