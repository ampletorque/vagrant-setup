from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config


@view_config(route_name='admin:markdown_guide',
             renderer='admin/markdown_guide.html')
def markdown_guide_view(request):
    return {}
