from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from ... import model

from . import NodePredicate


@view_config(route_name='node', renderer='update.html',
             custom_predicates=[NodePredicate(model.ProjectUpdate)])
def update_view(context, request):
    update = context.node
    assert update.project.published, \
        "cannot view update for unpublished project"
    return dict(
        update=update,
        project=update.project,
    )
