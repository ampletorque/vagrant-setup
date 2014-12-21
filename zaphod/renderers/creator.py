from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.renderers import render

from ..model import Creator


def creator_renderer(node, system):
    request = system['request']
    creator = node

    projects = [project for project in reversed(creator.projects)
                if project.published and project.is_live()]

    return render('creator.html',
                  dict(creator=creator, projects=projects),
                  request)


def includeme(config):
    config.add_node_renderer(creator_renderer, Creator)
