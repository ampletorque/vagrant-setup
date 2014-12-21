from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from .. import model


@view_config(route_name='creators', renderer='creators.html')
def creators_view(request):
    q = model.Session.query(model.Creator).\
        join(model.Node.aliases).\
        filter(model.Node.published == True).\
        order_by(model.Node.name)
    return dict(creators=q.all())
