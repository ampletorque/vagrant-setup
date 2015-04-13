from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

from sqlalchemy.sql import func, or_
from pyramid.view import view_config, view_defaults

from .base import BaseReportsView

from .... import model

log = logging.getLogger(__name__)


@view_defaults(permission='admin')
class AccountingReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:revenue',
                 renderer='admin/reports/revenue.html')
    def revenue(self):
        utcnow, start_date, end_date, start, end = self._range()
        # for a time range

        # crowdfunding fees, recognized at the time the project is successful
        # XXX
        q = model.Session.query(
            func.sum((model.CartItem.price_each * model.CartItem.qty_desired) +
                     model.CartItem.shipping_price) *
            model.Project.crowdfunding_fee_percent / 100).\
            join(model.CartItem.product).\
            join(model.Product.project).\
            filter(model.CartItem.stage == model.CartItem.CROWDFUNDING,
                   model.Project.end_time >= start,
                   model.Project.end_time < end)

        crowdfunding_fees = q.scalar() or 0

        # preorder commission, recognized at the time of order??
        # XXX
        q = model.Session.query(
            func.sum((model.CartItem.price_each * model.CartItem.qty_desired) +
                     model.CartItem.shipping_price) *
            model.Project.preorder_fee_percent / 100).\
            join(model.CartItem.product).\
            join(model.Product.project).\
            filter(model.CartItem.stage == model.CartItem.PREORDER,
                   model.Project.end_time >= start,
                   model.Project.end_time < end)

        preorder_fees = q.scalar() or 0

        # in-stock sales, recognized at the time of shipment
        # XXX
        q = model.Session.query(
            func.sum(model.CartItem.price_each * model.CartItem.qty_desired)).\
            filter(model.CartItem.stage == model.CartItem.STOCK,
                   model.CartItem.shipped_time >= start,
                   model.CartItem.shipped_time < end)

        stock_items = q.scalar() or 0

        # shipping revenue, recognized at the time of shipment
        # XXX
        q = model.Session.query(
            func.sum(model.CartItem.shipping_price)).\
            filter(model.CartItem.stage == model.CartItem.STOCK,
                   model.CartItem.shipped_time >= start,
                   model.CartItem.shipped_time < end)

        stock_shipping = q.scalar() or 0

        # fulfillment fees, recognized at the time of shipment
        # XXX
        q = model.Session.query(
            model.Product.fulfillment_fee,
            func.count(model.Shipment.id).label('num_shipments')).\
            join(model.Shipment.items).\
            join(model.CartItem.product).\
            filter(model.CartItem.stage != model.CartItem.STOCK,
                   model.Shipment.created_time >= start,
                   model.Shipment.created_time < end)

        subq = q.subquery()
        q = model.Session.query(
            func.sum(subq.c.fulfillment_fee * subq.c.num_shipments))

        fulfillment_fees = q.scalar() or 0

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
                 renderer='admin/reports/cogs.html')
    def cogs(self):
        utcnow, start_date, end_date, start, end = self._range()
        # for a time range

        # in-stock product cost
        q = model.Session.query(func.sum(model.Item.cost)).\
            join(model.Item.cart_item).\
            filter(model.CartItem.shipped_time >= start,
                   model.CartItem.shipped_time < end)
        stock_item_cost = q.scalar() or 0

        # outbound freight cost
        q = model.Session.query(func.sum(model.Shipment.cost)).\
            filter(model.Shipment.created_time >= start,
                   model.Shipment.created_time < end)
        outbound_shipping_cost = q.scalar() or 0

        total_cost = stock_item_cost + outbound_shipping_cost

        return {
            'stock_item_cost': stock_item_cost,
            'outbound_shipping_cost': outbound_shipping_cost,
            'total_cost': total_cost,
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:inventory',
                 renderer='admin/reports/inventory.html')
    def inventory(self):
        utcnow, start_date, end_date, start, end = self._range()
        # for a certain date, show:

        # confirmed inventory value
        base_q = model.Session.query(func.sum(model.Item.cost)).\
            outerjoin(model.Item.cart_item).\
            filter(model.Item.create_time < start).\
            filter(or_(model.Item.destroy_time == None,
                       model.Item.destroy_time > end)).\
            filter(or_(model.CartItem.shipped_time == None,
                       model.CartItem.shipped_time > end))

        # unconfirmed inventory value
        confirmed_q = base_q.\
            filter(model.Item.vendor_invoice_item_id != None)
        confirmed_value = confirmed_q.scalar() or 0

        unconfirmed_q = base_q.\
            filter(model.Item.vendor_invoice_item_id == None)
        unconfirmed_value = unconfirmed_q.scalar() or 0

        total_value = confirmed_value + unconfirmed_value

        # top projects by inventory value
        project_q = base_q.\
            join(model.Item.acquisition).\
            join(model.Acquisition.sku).\
            join(model.SKU.product).\
            join(model.Product.project).\
            add_entity(model.Project).\
            group_by(model.Project.id).\
            order_by(func.sum(model.Item.cost).desc())
        value_by_project = [(project, value) for value, project in project_q]

        return {
            'start_date': start_date,
            'end_date': end_date,
            'confirmed_value': confirmed_value,
            'unconfirmed_value': unconfirmed_value,
            'total_value': total_value,
            'value_by_project': value_by_project,
        }

    @view_config(route_name='admin:reports:cashflow',
                 renderer='admin/reports/cashflow.html')
    def cashflow(self):
        utcnow, start_date, end_date, start, end = self._range()

        # for a time range, show
        # total payments in by type
        # total payments out to creators

        return {
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:payments',
                 renderer='admin/reports/payments.html')
    def payments(self):
        utcnow, start_date, end_date, start, end = self._range()

        # for a time range, show payments captured by (gateway, type)
        q = model.Session.query(model.PaymentGateway,
                                model.CreditCardPayment.card_type_code,
                                func.sum(model.CreditCardPayment.amount)).\
            join(model.CreditCardPayment.method).\
            join(model.PaymentMethod.gateway).\
            filter(model.CreditCardPayment.captured_time != None,
                   model.CreditCardPayment.captured_time >= start,
                   model.CreditCardPayment.captured_time < end).\
            group_by(model.PaymentGateway.id,
                     model.CreditCardPayment.card_type_code)

        payments = {}
        card_type_codes = set()
        for gateway, card_type_code, amount in q:
            card_type_codes.add(card_type_code)
            gw_payments = payments.setdefault(gateway, {})
            gw_payments[card_type_code] = amount

        card_types = list(card_type_codes)

        payments = payments.items()
        payments.sort(key=lambda row: row[0].id)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'payments': payments,
            'card_types': card_types,
        }

    @view_config(route_name='admin:reports:chargebacks',
                 renderer='admin/reports/chargebacks.html')
    def chargebacks(self):
        utcnow, start_date, end_date, start, end = self._range()

        q = model.Session.query(model.CreditCardPayment).\
            filter(model.CreditCardPayment.chargeback_state != None,
                   model.CreditCardPayment.created_time >= start,
                   model.CreditCardPayment.created_time < end)

        chargeback_payments = q.all()

        # number of chargebacks
        chargeback_count = len(chargeback_payments)

        # $ total of chargebacks
        chargeback_amount = sum(pp.amount for pp in chargeback_payments)

        # chargeback rate as % of transactions
        total_count = model.Session.query(model.CreditCardPayment).\
            filter(model.CreditCardPayment.amount > 0,
                   model.CreditCardPayment.created_time >= start,
                   model.CreditCardPayment.created_time < end).\
            count()

        # chargeback rate as % of payment amounts
        total_amount = model.Session.query(
            func.sum(model.CreditCardPayment.amount)).\
            filter(model.CreditCardPayment.created_time >= start,
                   model.CreditCardPayment.created_time < end).\
            scalar()

        # list of payments with chargebacks, linked to order pages

        return {
            'start_date': start_date,
            'end_date': end_date,

            'chargeback_payments': chargeback_payments,
            'chargeback_count': chargeback_count,
            'chargeback_amount': chargeback_amount,
            'total_count': total_count,
            'total_amount': total_amount,
        }
