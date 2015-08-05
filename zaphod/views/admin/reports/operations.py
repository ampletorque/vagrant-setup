from pyramid.view import view_config, view_defaults
from sqlalchemy.sql import func, not_

from .base import BaseReportsView

from .... import model


@view_defaults(permission='admin')
class OperationsReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:warehouse-transactions',
                 renderer='admin/reports/warehouse_transactions.html')
    def warehouse_transactions(self):
        utcnow, start_date, end_date, start, end = self._range()

        # positive inventory adjustment count and $ value
        q = model.Session.query(
            func.count(model.InventoryAdjustment.id.distinct()),
            func.sum(model.Item.cost)).\
            join(model.InventoryAdjustment.items).\
            filter(model.InventoryAdjustment.qty_diff > 0).\
            filter(model.InventoryAdjustment.acquisition_time >= start,
                   model.InventoryAdjustment.acquisition_time < end)
        positive_adjustment_count, positive_adjustment_value = q.first()

        # negative inventory adjustment count and $ value
        q = model.Session.query(
            func.count(model.InventoryAdjustment.id.distinct()),
            func.sum(model.Item.cost)).\
            join(model.Item.destroy_adjustment).\
            filter(model.InventoryAdjustment.qty_diff < 0).\
            filter(model.InventoryAdjustment.acquisition_time >= start,
                   model.InventoryAdjustment.acquisition_time < end)
        negative_adjustment_count, negative_adjustment_value = q.first()

        # shipment in count
        q = model.Session.query(func.count(model.VendorShipment.id.distinct()),
                                func.count(model.Item.id.distinct())).\
            join(model.VendorShipment.items).\
            join(model.VendorShipmentItem.items).\
            filter(model.VendorShipment.created_time >= start,
                   model.VendorShipment.created_time < end)
        inbound_shipment_count, inbound_item_count = q.first()

        # shipment out count
        q = model.Session.query(func.count(model.Shipment.id.distinct()),
                                func.sum(model.CartItem.qty_desired)).\
            join(model.Shipment.items).\
            filter(model.Shipment.created_time >= start,
                   model.Shipment.created_time < end)
        outbound_shipment_count, outbound_item_count = q.first()

        return {
            'start_date': start_date,
            'end_date': end_date,

            'positive_adjustment_count': positive_adjustment_count,
            'positive_adjustment_value': positive_adjustment_value,
            'negative_adjustment_count': negative_adjustment_count,
            'negative_adjustment_value': negative_adjustment_value,
            'inbound_shipment_count': inbound_shipment_count,
            'inbound_item_count': inbound_item_count,
            'outbound_shipment_count': outbound_shipment_count,
            'outbound_item_count': outbound_item_count,
        }

    @view_config(route_name='admin:reports:project-open-items',
                 renderer='admin/reports/project_open_items.html')
    def project_open_items(self):
        q = model.Session.query(model.Project,
                                func.count(model.Order.id.distinct())).\
            join(model.Order.cart).\
            join(model.Cart.items).\
            join(model.CartItem.product).\
            join(model.Product.project).\
            filter(not_(model.CartItem.status.in_(['failed', 'cancelled',
                                                   'shipped', 'abandoned']))).\
            group_by(model.Project.id)

        by_project = q.all()

        return {
            'by_project': by_project,
        }
