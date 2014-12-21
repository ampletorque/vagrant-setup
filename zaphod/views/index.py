from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config


@view_config(route_name='index', renderer='index.html')
def index_view(request):
    return {}
