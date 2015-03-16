from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ... import model


def update_view(update, system):
    assert update.project.published, \
        "cannot view update for unpublished project"
    return dict(
        update=update,
        project=update.project,
    )


def includeme(config):
    config.add_node_view(update_view, model.ProjectUpdate,
                         renderer='update.html')
