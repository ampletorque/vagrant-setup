from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.renderers import render

from ..model import Project


def project_renderer(project, system):
    request = system['request']
    suffix = system['suffix']

    if suffix:
        raise NotImplementedError

    return render('project.html', dict(project=project), request)


def includeme(config):
    config.add_node_renderer(project_renderer, Project, accept_suffix=True)
