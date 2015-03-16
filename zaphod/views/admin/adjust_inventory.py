from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from formencode import Schema, validators

from pyramid_uniform import Form, FormRenderer

from ... import model


class AdjustInventoryForm(Schema):
    allow_extra_fields = False
    old_qty = validators.Int(not_empty=True)
    new_qty = validators.Int(not_empty=True)
    reason = validators.String(not_empty=True)


class AdjustInventoryView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:adjust-inventory',
                 renderer='admin/adjust_inventory.html',
                 permission='authenticated')
    def index(self):
        request = self.request
        id = request.matchdict['id']
        sku = model.SKU.get(id)

        reasons = [("move", "Moving items between SKUs"),
                   ('retc', "Returned to Vendor (Credit)"),
                   ('retd', 'Returned to Vendor (Defective)'),
                   ('cret', "Returned by Customer"),
                   ("manl", "Manual Restock"),
                   ("corr", "Stock Correction"),
                   ("misc", "Other")]

        form = Form(request, AdjustInventoryForm)
        if form.validate():
            if sku.qty != form.data['old_qty']:
                request.flash("In-stock qty has changed since page load. "
                              "Please re-check qty.", 'error')
                raise HTTPFound(location=request.current_route_url())

            qty_diff = form.data['new_qty'] - sku.qty
            if qty_diff != 0:
                sku.adjust_qty(qty_diff=qty_diff,
                               reason=dict(reasons)[form.data['reason']],
                               user=request.user)
                request.flash("SKU qty updated.", 'success')
                return HTTPFound(
                    location=request.route_url('admin:product:skus',
                                               id=sku.product_id))
            else:
                request.flash("Qty was not changed.", 'error')

        return {
            'sku': sku,
            'reasons': reasons,
            'renderer': FormRenderer(form),
        }
