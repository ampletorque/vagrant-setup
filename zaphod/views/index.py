from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from .. import model


def get_project(name):
    return model.Session.query(model.Project).\
        filter_by(name=name, published=True).\
        first()


def load_projects(rows):
    all = []
    for row in rows:
        these = []
        for name in row:
            project = get_project(name)
            if project:
                these.append(project)
        all.append(these)
    return all


@view_config(route_name='index', renderer='index.html')
def index_view(request):
    def get_groups():
        recently_launched = [
            [
                'Vinny by Plywerk',
                'Quiet Linear Mechanical Keyboard Switch',
            ],
        ]

        recently_funded = [
            [
                'Librem 15: A Free/Libre Software Laptop That '
                'Respects Your Essential Freedoms',
                'USB Armory: Open Source USB Stick Computer',
            ],
            [
                'A Weather Walked In',
                'Goodwell: Open Source Modern Toothbrush',
            ],
            [
                'Hydrogen: Next-Generation Supercapacitor-Powered '
                'Portable Speaker',
                'Hack-E-Bot: affordable + open source robot for all',
                'Handmade Cedar SUP Paddles, Boards and DIY Kits',
            ],
        ]

        crowd_favorites = [
            [
                'The Portland Press',
                'Circuit Stickers',
                'Novena',
            ],
        ]

        return [
            ('Recently Launched', load_projects(recently_launched)),
            ('Recently Funded', load_projects(recently_funded)),
            ('Crowd Favorites', load_projects(crowd_favorites)),
        ]

    return dict(widget='blue', get_groups=get_groups)
