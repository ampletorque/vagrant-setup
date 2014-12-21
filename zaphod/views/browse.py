from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from .. import model


@view_config(route_name='browse', renderer='browse.html')
def browse_view(request):
    projects = model.Session.query(model.Project).\
        filter_by(published=True, listed=True)
    return dict(projects=projects)
