from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def includeme(config):
    config.add_route('admin', '/')

    config.add_route('admin:creators', '/creators')
    config.add_route('admin:projects', '/projects')
    config.add_route('admin:users', '/users')
