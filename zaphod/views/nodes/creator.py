from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ... import model


def creator_view(creator, system):
    projects = [project.id for project in reversed(creator.projects)
                if project.published and project.is_live()]

    return dict(creator=creator, projects=projects)


def includeme(config):
    config.add_node_view(creator_view, model.Creator, renderer='creator.html')
