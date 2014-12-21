from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def includeme(config):
    config.add_route('index', '/')
    config.add_route('browse', '/browse')

    # This needs to stay the last route registered.
    config.add_route('node', '/*path')

    config.scan('.')
