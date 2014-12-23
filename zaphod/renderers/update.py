from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.renderers import render

from .. import model


def update_renderer(update, system):
    request = system['request']
    assert update.project.published, \
        "cannot view update for unpublished project"
    return render('update.html', dict(
        update=update,
        project=update.project,
    ), request)


def includeme(config):
    config.add_node_renderer(update_renderer, model.ProjectUpdate)
