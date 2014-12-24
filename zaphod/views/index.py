from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from .. import model


def get_project(name):
    return model.Session.query(model.Project).\
        filter_by(name=name, published=True).\
        one()


@view_config(route_name='index', renderer='index.html')
def index_view(request):
    recently_launched = [
        [
            get_project('USB Armory: Open Source USB Stick Computer'),
            get_project('A Weather Walked In'),
        ],
        [
            get_project('Librem 15: A Free/Libre Software Laptop That '
                        'Respects Your Essential Freedoms'),
            get_project('High Tech Plant Operating System'),
        ],
    ]

    recently_funded = [
        [
            get_project('Goodwell: Open Source Modern Toothbrush'),
            get_project('Circuit Stickers Holiday Greeting Card'),
        ],
        [
            get_project('Hydrogen: Next-Generation Supercapacitor-Powered '
                        'Portable Speaker'),
            get_project('Hack-E-Bot: affordable + open source robot for all'),
            get_project('Handmade Cedar SUP Paddles, Boards and DIY Kits'),
        ],
    ]

    crowd_favorites = [
        [
            get_project('The Portland Press'),
            get_project('Circuit Stickers'),
            get_project('Novena'),
        ],
    ]

    groups = [
        ('Recently Launched', recently_launched),
        ('Recently Funded', recently_funded),
        ('Crowd Favorites', crowd_favorites),
    ]
    return dict(groups=groups)
