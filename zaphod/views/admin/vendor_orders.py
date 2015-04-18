from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, validators

from ... import model, custom_validators

from ...admin import BaseEditView, BaseListView, BaseCreateView


@view_defaults(route_name='admin:vendor-order',
               renderer='admin/vendor_order.html', permission='admin')
@lift()
class VendorOrderEditView(BaseEditView):
    cls = model.VendorOrder

    class UpdateForm(Schema):
        "Schema for validating vendor order update form."
        loaded_time = validators.Number(not_empty=True)
        new_comment = custom_validators.CommentBody()

    @view_config(route_name='admin:vendor-order:mark-sent')
    def mark_sent(self):
        request = self.request
        vo = self._get_object()
        self._touch_object(vo)
        vo.status = 'sent'
        vo.placed_by = request.user
        vo.placed_time = model.utcnow()
        request.flash("Marked order as sent.", 'success')
        return HTTPFound(location=request.route_url('admin:vendor-order',
                                                    id=vo.id))

    @view_config(route_name='admin:vendor-order:mark-confirmed')
    def mark_confirmed(self):
        request = self.request
        vo = self._get_object()
        self._touch_object(vo)
        vo.status = 'conf'
        request.flash("Marked order as confirmed.", 'success')
        return HTTPFound(location=request.route_url('admin:vendor-order',
                                                    id=vo.id))


@view_defaults(route_name='admin:vendor-orders',
               renderer='admin/vendor_orders.html', permission='admin')
@lift()
class VendorOrderListView(BaseListView):
    cls = model.VendorOrder


@view_defaults(route_name='admin:vendor-orders:new',
               renderer='admin/vendor_orders_new.html', permission='admin')
@lift()
class VendorOrderCreateView(BaseCreateView):
    cls = model.VendorOrder
    obj_route_name = 'admin:vendor-order'

    class CreateForm(Schema):
        allow_extra_fields = False
        vendor_id = validators.Int(not_empty=True)
