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

        # show
        # stock inventory adjustment count and $ value
        # shipment in count
        # shipment out count

        return {
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:delays',
                 renderer='admin/reports/delays.html',
                 permission='authenticated')
    def delays(self):
        utcnow, start_date, end_date, start, end = self._range()

        # for given time period, show:
        # - orders which were shipped
        #    - late
        #    - on time
        # - "most late" orders

        return {
            'start_date': start,
            'end_date': end,
        }

    # XXX consider also a 'problem project' report that shows the worst
    # currently overdue projects and projects that are in need of an update
