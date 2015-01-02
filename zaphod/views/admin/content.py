from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config


@view_config(route_name='admin:content', renderer='admin/content.html',
             permission='authenticated')
def content_view(request):
    return {}
