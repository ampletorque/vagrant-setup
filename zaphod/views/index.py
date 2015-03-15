from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from .. import model


def load_projects(rows):
    return rows
    all = []
    for row in rows:
        these = []
        for project_id in row:
            project = model.Project.get(project_id)
            if project:
                these.append(project)
        all.append(these)
    return all


@view_config(route_name='index', renderer='index.html')
def index_view(request):
    def get_groups():
        recently_launched = [
            [
                1490,  # plywerk
                1492,  # key switches
            ],
        ]

        recently_funded = [
            [
                1364,  # librem
                1329,  # usb armory
            ],
            [
                1430,  # a weather walked in
                1224,  # goodwell
                1259,  # hydrogen
            ],
        ]

        crowd_favorites = [
            [
                236,  # portland press
                746,  # circuit stickers
                962,  # novena
            ],
        ]

        return [
            ('Recently Launched', load_projects(recently_launched)),
            ('Recently Funded', load_projects(recently_funded)),
            ('Crowd Favorites', load_projects(crowd_favorites)),
        ]

    return dict(get_groups=get_groups)
