from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from .base import BaseReportsView


class OperationsReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:warehouse-transactions',
                 renderer='admin/reports/warehouse_transactions.html',
                 permission='authenticated')
    def warehouse_transactions(self):
        utcnow, start_date, end_date, start, end = self._range()

        return {
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:delays',
                 renderer='admin/reports/delays.html',
                 permission='authenticated')
    def delays(self):
        utcnow, start_date, end_date, start, end = self._range()

        return {
            'start_date': start,
            'end_date': end,
        }
