from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ... import model

from . import NodePredicate


def update_view(context, request):
    update = context.node
    assert update.project.published, \
        "cannot view update for unpublished project"
    return dict(
        update=update,
        project=update.project,
    )


def includeme(config):
    config.add_view(update_view,
                    custom_predicates=[NodePredicate(model.ProjectUpdate)],
                    renderer='update.html')
