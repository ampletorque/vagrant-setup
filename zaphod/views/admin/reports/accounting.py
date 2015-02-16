from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from sqlalchemy.sql import func

from .... import model

from .base import BaseReportsView


class AccountingReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:revenue',
                 renderer='admin/reports/revenue.html',
                 permission='authenticated')
    def revenue(self):
        utcnow = model.utcnow()

        # crowdfunding fees, recognized at the time the project is successful

        # preorder commission, recognized at the time of order??

        # in-stock sales, recognized at the time of shipment

        # shipping revenue, recognized at the time of shipment

        # fulfillment fees, recognized at the time of shipment

        return {
        }

    @view_config(route_name='admin:reports:cogs',
                 renderer='admin/reports/cogs.html',
                 permission='authenticated')
    def cogs(self):
        utcnow = model.utcnow()

        # in-stock product cost
        # fulfillment cost
        # outbound freight cost

        return {
        }

    @view_config(route_name='admin:reports:inventory',
                 renderer='admin/reports/inventory.html',
                 permission='authenticated')
    def inventory(self):
        utcnow = model.utcnow()

        # as of a certain date, show:
        # confirmed inventory value
        # unconfirmed inventory value

        # top projects by inventory value

        return {
        }

    @view_config(route_name='admin:reports:cashflow',
                 renderer='admin/reports/cashflow.html',
                 permission='authenticated')
    def cashflow(self):

        # for a time range, show:
        # total payments in by type
        # total payments out to creators

        return {
        }

    @view_config(route_name='admin:reports:payments',
                 renderer='admin/reports/payments.html',
                 permission='authenticated')
    def payments(self):
        return {
        }
