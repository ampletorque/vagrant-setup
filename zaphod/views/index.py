from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from pyramid.settings import asbool


@view_config(route_name='index', renderer='index.html')
def index_view(request):
    if asbool(request.registry.settings.get('testing')):
        def get_groups():
            return [
                ('Recently Launched', []),
                ('Recently Funded', []),
                ('Crowd Favorites', []),
            ]
    else:
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
                ('Recently Launched', recently_launched),
                ('Recently Funded', recently_funded),
                ('Crowd Favorites', crowd_favorites),
            ]

    return dict(get_groups=get_groups)
