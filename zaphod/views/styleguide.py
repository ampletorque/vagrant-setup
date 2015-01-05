from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from formencode import Schema
from pyramid_uniform import Form, FormRenderer
from pyramid.view import view_config


@view_config(route_name='styleguide', renderer='styleguide.html')
def styleguide_view(request):
    form = Form(request, schema=Schema())
    return dict(renderer=FormRenderer(form))
