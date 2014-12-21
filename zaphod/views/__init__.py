from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def includeme(config):
    config.include('.admin', route_prefix='/admin')

    config.add_route('index', '/')

    config.add_route('launch', '/launch')
    config.add_route('about', '/about')

    config.add_route('cart', '/cart')

    config.add_route('browse', '/browse')
    config.add_route('search', '/search')

    # User scaffolding routes
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('forgot-password', '/forgot-password')
    config.add_route('forgot-reset', '/forgot-reset')
    config.add_route('account', '/account')

    # This needs to stay the last route registered.
    config.add_route('node', '/*path')

    config.scan('.')
