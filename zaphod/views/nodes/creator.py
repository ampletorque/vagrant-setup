from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ... import model

from . import NodePredicate


def creator_view(context, request):
    creator = context.node
    projects = [project.id for project in reversed(creator.projects)
                if project.published and project.is_live()]

    return dict(creator=creator, projects=projects)


def includeme(config):
    config.add_view(creator_view,
                    route_name='node',
                    custom_predicates=[NodePredicate(model.Creator)],
                    renderer='creator.html')
