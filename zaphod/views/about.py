from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config


@view_config(route_name='about', renderer='about.html')
def about_view(request):
    return {}
