from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from ... import model


@view_config(route_name='admin:users', renderer='admin/users.html',
             permission='authenticated')
def users_view(request):
    q = model.Session.query(model.User)
    return dict(users=q.all())
