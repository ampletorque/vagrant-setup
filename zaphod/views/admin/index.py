from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config


@view_config(route_name='admin', renderer='admin/index.html',
             permission='authenticated')
def index_view(request):
    return {}
