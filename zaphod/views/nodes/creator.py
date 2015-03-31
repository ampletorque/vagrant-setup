from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from ... import model

from . import NodePredicate


@view_config(route_name='node', renderer='creator.html',
             custom_predicates=[NodePredicate(model.Creator)])
def creator_view(context, request):
    creator = context.node
    projects = [project.id for project in reversed(creator.projects)
                if project.published and project.is_live()]

    return dict(creator=creator, projects=projects)
