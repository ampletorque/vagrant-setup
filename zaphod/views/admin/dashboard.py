from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config


@view_config(route_name='admin:dashboard', renderer='admin/dashboard.html',
             permission='authenticated')
def dashboard_view(request):
    return {}
