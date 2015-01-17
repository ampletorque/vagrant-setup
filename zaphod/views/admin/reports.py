from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config


class ReportsView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:reports',
                 renderer='admin/reports.html',
                 permission='authenticated')
    def index(self):
        return {}
