from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config, view_defaults
from sqlalchemy.sql import func

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

    @view_config(route_name='admin:reports:delays',
                 renderer='admin/reports/delays.html')
    def delays(self):
        utcnow, start_date, end_date, start, end = self._range()

        delay_bucket = func.round(func.datediff(
            model.CartItem.shipped_time,
            model.CartItem.expected_ship_time), -1).label('delay')
        q = model.Session.query(
            delay_bucket,
            func.count(model.CartItem.id.distinct())).\
            filter(model.CartItem.expected_ship_time != None,
                   model.CartItem.shipped_time >= start,
                   model.CartItem.shipped_time < end).\
            group_by(delay_bucket)
        delay_count = q.all()
        total_count = sum(count for delay, count in delay_count)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'delay_count': delay_count,
            'total_count': total_count,
        }

    @view_config(route_name='admin:reports:project-delays',
                 renderer='admin/reports/project_delays.html')
    def project_delays(self):
        utcnow, start_date, end_date, start, end = self._range()

        delay = func.datediff(
            func.ifnull(model.CartItem.shipped_time, utcnow),
            model.CartItem.expected_ship_time)
        max_delay = func.max(delay).label('worst')
        avg_delay = func.avg(delay).label('average')
        q = model.Session.query(model.Project, max_delay, avg_delay).\
            filter(model.CartItem.expected_ship_time != None,
                   model.CartItem.expected_ship_time < utcnow).\
            join(model.CartItem.product).\
            join(model.Product.project).\
            filter(model.CartItem.status.in_(['shipped', 'in process',
                                              'waiting'])).\
            filter(model.CartItem.stage == model.CartItem.CROWDFUNDING).\
            group_by(model.Project.id).\
            order_by(avg_delay.desc())
        projects = q.all()

        return {
            'projects': projects,
        }

    # XXX consider also a 'problem project' report that shows the worst
    # currently overdue projects and projects that are in need of an update
