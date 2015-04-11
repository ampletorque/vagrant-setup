from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, ForEach, NestedVariables, validators
from pyramid.httpexceptions import HTTPFound
from pyramid_uniform import Form, FormRenderer

from ... import model

from ...admin import BaseEditView


class ItemSchema(Schema):
    allow_extra_fields = False
    id = validators.Int(not_empty=True, min=0)
    qty_invoiced = validators.Int(not_empty=True, min=0)
    cost_each = validators.Number(not_empty=True, min=0)


class InvoiceForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    invoice_num = validators.UnicodeString(not_empty=True)
    invoice_date = validators.DateConverter()

    shipping_date = validators.DateConverter()
    shipping_cost = validators.Number(not_empty=True, min=0)

    tax = validators.Number(not_empty=True, min=0)
    drop_ship_fee = validators.Number(not_empty=True, min=0)
    discount = validators.Number(not_empty=True, min=0)
    discount_applies = validators.Bool()
    bank_fee = validators.Number(not_empty=True, min=0)

    items = ForEach(ItemSchema)


@view_defaults(route_name='admin:vendor-invoice',
               renderer='admin/vendor_invoice.html', permission='admin')
@lift()
class VendorInvoiceEditView(BaseEditView):
    cls = model.VendorInvoice

    UpdateForm = InvoiceForm

    def _update_object(self, form, obj):
        request = self.request
        # XXX

        request.flash('Saved changes.', 'success')

    @view_config(route_name='admin:vendor-order:receive-invoice',
                 renderer='admin/vendor_invoice_receive.html')
    def receive_invoice(self):
        request = self.request
        vendor_order = model.VendorOrder.get(request.matchdict['id'])

        form = Form(request, InvoiceForm)
        if form.validate():
            vendor_invoice = self.cls(vendor_order=vendor_order)
            for item_params in form.data.pop('items'):
                vendor_invoice.items.append(model.VendorInvoiceItem(
                    qty_invoiced=item_params['qty'],
                    cost_each=item_params['cost_each'],
                ))

            form.bind(vendor_invoice)
            request.flash("Received invoice.", 'success')
            return HTTPFound(
                location=request.route_url('admin:vendor-invoice',
                                           id=vendor_invoice.id))

        return {
            'vendor_order': vendor_order,
            'renderer': FormRenderer(form),
        }
