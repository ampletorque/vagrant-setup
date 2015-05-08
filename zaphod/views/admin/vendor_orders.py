from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, ForEach, NestedVariables, validators
from pyramid_uniform import Form, FormRenderer

from ... import model, custom_validators

from ...admin import BaseEditView, BaseListView, BaseCreateView


class AddItemForm(Schema):
    allow_extra_fields = False
    product_id = validators.Int(not_empty=True)
    value_ids = ForEach(validators.Int(not_empty=True))
    qty = validators.Int(not_empty=True, min=1, max=999)


class UpdateItemSchema(Schema):
    id = validators.Int(not_empty=True)
    qty_ordered = validators.Int(not_empty=True, min=1)
    cost = custom_validators.Money()


@view_defaults(route_name='admin:vendor-order',
               renderer='admin/vendor_order.html', permission='admin')
@lift()
class VendorOrderEditView(BaseEditView):
    cls = model.VendorOrder

    class UpdateForm(Schema):
        "Schema for validating vendor order update form."
        pre_validators = [NestedVariables()]
        reference = validators.UnicodeString()
        description = validators.UnicodeString()
        items = ForEach(UpdateItemSchema)
        new_comment = custom_validators.CommentBody()

    def _process_add_item(self, form, vo):
        request = self.request
        self._touch_object(vo)
        product = model.Product.get(form.data['product_id'])
        sku = model.sku_for_option_value_ids(product,
                                             form.data['value_ids'])

        voi = model.VendorOrderItem(
            sku=sku,
            qty_ordered=form.data['qty'],
        )
        vo.items.append(voi)
        request.flash("Added item %s." % voi.sku.product.name, 'success')

    @view_config(route_name='admin:vendor-order:add-item',
                 renderer='admin/vendor_order_add_item.html')
    def add_item(self):

        request = self.request
        vo = self._get_object()

        form = Form(request, AddItemForm)
        if form.validate():
            self._process_add_item(form, vo)
            return HTTPFound(location=request.route_url('admin:vendor-order',
                                                        id=vo.id))

        return {
            'obj': vo,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:vendor-order:add-item',
                 request_method='POST', xhr=True, renderer='json')
    def add_item_ajax(self):
        request = self.request
        vo = self._get_object()
        form = Form(request, AddItemForm)
        if form.validate():
            self._process_add_item(form, vo)
            return {
                'status': 'ok',
                'location': request.route_url('admin:vendor-order', id=vo.id),
            }
        else:
            return {
                'status': 'fail',
                'errors': form.errors,
            }

    @view_config(route_name='admin:vendor-order:remove-item')
    def remove_item(self):
        request = self.request
        vo = self._get_object()
        voi = model.VendorOrderItem.get(request.matchdict['item_id'])
        assert voi.order == vo
        request.flash("Removed '%s' from order." % voi.sku.product.name,
                      'success')
        assert voi.qty_received == 0
        assert voi.qty_invoiced == 0
        model.Session.delete(voi)
        self._touch_object(vo)
        return HTTPFound(location=request.route_url('admin:vendor-order',
                                                    id=vo.id))

    def _update_object(self, form, obj):
        for item_params in form.data.pop('items'):
            item = model.VendorOrderItem.get(item_params['id'])
            assert item.order == obj
            item.qty_ordered = item_params['qty_ordered']
            item.cost = item_params['cost']
        BaseEditView._update_object(self, form, obj)

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
