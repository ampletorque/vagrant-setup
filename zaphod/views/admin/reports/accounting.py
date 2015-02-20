from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy.sql import func
from pyramid.view import view_config

from .base import BaseReportsView

from .... import model


class AccountingReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:revenue',
                 renderer='admin/reports/revenue.html',
                 permission='authenticated')
    def revenue(self):
        utcnow, start_date, end_date, start, end = self._range()
        # for a time range

        # crowdfunding fees, recognized at the time the project is successful
        # XXX
        q = model.Session.query(
            func.sum((model.CartItem.price_each * model.CartItem.qty_desired) +
                     model.CartItem.shipping_price) *
            model.Project.fee_percent / 100).\
            join(model.CartItem.product).\
            join(model.Product.project).\
            filter(model.Project.end_time >= start,
                   model.Project.end_time < end)

        crowdfunding_fees = q.scalar() or 0

        # preorder commission, recognized at the time of order??
        # XXX
        preorder_fees = 0

        # in-stock sales, recognized at the time of shipment
        # XXX
        q = model.Session.query(
            func.sum(model.CartItem.price_each * model.CartItem.qty_desired)).\
            filter(model.CartItem.shipped_date >= start,
                   model.CartItem.shipped_date < end)

        stock_items = q.scalar() or 0

        # shipping revenue, recognized at the time of shipment
        # XXX
        q = model.Session.query(
            func.sum(model.CartItem.shipping_price)).\
            filter(model.CartItem.shipped_date >= start,
                   model.CartItem.shipped_date < end)

        stock_shipping = q.scalar()

        # fulfillment fees, recognized at the time of shipment
        # XXX
        fulfillment_fees = 0

        total = (crowdfunding_fees + fulfillment_fees + preorder_fees +
                 stock_items + stock_shipping)

        return {
            'crowdfunding_fees': crowdfunding_fees,
            'fulfillment_fees': fulfillment_fees,
            'preorder_fees': preorder_fees,
            'stock_items': stock_items,
            'stock_shipping': stock_shipping,
            'total': total,
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:cogs',
                 renderer='admin/reports/cogs.html',
                 permission='authenticated')
    def cogs(self):
        utcnow, start_date, end_date, start, end = self._range()
        # for a time range

        # in-stock product cost
        # XXX
        stock_items = 0

        # outbound freight cost
        # XXX
        shipping = 0

        total = stock_items + shipping

        return {
            'stock_items': stock_items,
            'shipping': shipping,
            'total': total,
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:inventory',
                 renderer='admin/reports/inventory.html',
                 permission='authenticated')
    def inventory(self):
        # for a certain date, show:

        # confirmed inventory value
        # unconfirmed inventory value

        # top projects by inventory value

        return {
        }

    @view_config(route_name='admin:reports:cashflow',
                 renderer='admin/reports/cashflow.html',
                 permission='authenticated')
    def cashflow(self):
        utcnow, start_date, end_date, start, end = self._range()

        # for a time range, show:
        # total payments in by type
        # total payments out to creators

        return {
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:payments',
                 renderer='admin/reports/payments.html',
                 permission='authenticated')
    def payments(self):
        utcnow, start_date, end_date, start, end = self._range()
        # for a time range, show:
        # payments by cc type
        # payments by gateway
        return {
            'start_date': start_date,
            'end_date': end_date,
        }
