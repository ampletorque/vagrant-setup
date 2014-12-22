from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from ... import model


@view_config(route_name='admin:projects', renderer='admin/projects.html',
             permission='authenticated')
def projects_view(request):
    q = model.Session.query(model.Project)
    return dict(projects=q.all())
