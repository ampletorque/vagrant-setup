from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, ForEach, NestedVariables, validators

from ... import model

from ...admin import BaseEditView


class ItemForm(Schema):
    qty = validators.Int(not_empty=True, min=0)
    id = validators.Int(not_empty=True, min=0)


@view_defaults(route_name='admin:vendor-shipment',
               renderer='admin/vendor_shipment.html', permission='admin')
@lift()
class VendorShipmentEditView(BaseEditView):
    cls = model.VendorShipment

    class UpdateForm(Schema):
        "Schema for validating vendor shipment update form."
        pre_validators = [NestedVariables()]
        description = validators.UnicodeString()
        items = ForEach(ItemForm)

    def _update_obj(self, form, obj):
        request = self.request
        for item_params in form.data.pop('items'):
            vsi = model.VendorShipmentItem.get(item_params['id'])
            vsi.adjust_qty(item_params['qty'])
        form.bind(obj)
        request.flash('Saved changes.', 'success')
