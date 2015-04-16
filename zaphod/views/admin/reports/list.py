from pyramid.view import view_config


class ReportsView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:reports',
                 renderer='admin/reports/list.html',
                 permission='admin')
    def list(self):
        return {}
