from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from .base import BaseReportsView


class OperationsReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:warehouse-transactions',
                 renderer='admin/reports/warehouse_transactions.html',
                 permission='authenticated')
    def warehouse_transactions(self):
        return {
        }

    @view_config(route_name='admin:reports:delays',
                 renderer='admin/reports/delays.html',
                 permission='authenticated')
    def delays(self):
        return {
        }
