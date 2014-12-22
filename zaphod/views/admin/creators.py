from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from ... import model


@view_config(route_name='admin:creators', renderer='admin/creators.html',
             permission='authenticated')
def creators_view(request):
    q = model.Session.query(model.Creator)
    return dict(creators=q.all())
