from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def includeme(config):
    config.include('.error')

    config.include('.admin', route_prefix='/admin')

    config.add_route('index', '/')

    config.add_route('sitemap', '/sitemap.xml')

    config.add_route('launch', '/launch')
    config.add_route('contact', '/contact')
    config.add_route('about', '/about')
    config.add_route('security', '/security')
    config.add_route('styleguide', '/styleguide')
    config.add_route('subscribe', '/subscribe')
    config.add_route('providers', '/providers')

    config.add_route('questions', '/questions')
    config.add_route('how', '/how-it-works')
    config.add_route('logistics', '/logistics')
    config.add_route('funding', '/funding')
    config.add_route('campaign-information', '/campaign-information')
    config.add_route('user-experience', '/user-experience')

    config.add_route('cart', '/cart')
    config.add_route('cart:add', '/cart/add')
    config.add_route('cart:remove', '/cart/remove')
    config.add_route('cart:update', '/cart/update')
    config.add_route('cart:confirmed', '/cart/complete')

    config.add_route('browse', '/browse')
    config.add_route('search', '/search')
    config.add_route('prelaunch', '/prelaunch')
    config.add_route('crowdfunding', '/crowdfunding')
    config.add_route('available', '/available')
    config.add_route('archive', '/archive')

    config.include('.browse')
    config.include('.search')

    config.add_route('creators', '/creators')

    # User scaffolding routes
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('forgot-password', '/forgot-password')
    config.add_route('forgot-reset', '/forgot-reset')
    config.add_route('account', '/account')
    config.add_route('order', '/account/order/{id}')
    config.add_route('settings', '/account/settings')
    config.add_route('profile', '/people/{path}')

    config.add_route('update-payment', '/update-payment')

    config.add_route('pinset', '/pinset/{id}.jpg')

    config.add_route('fail', '/fail')

    def fail_view(request):
        raise Exception('fail!')

    config.add_view(fail_view, route_name='fail', permission='authenticated')

    # This needs to stay the last route registered.
    config.add_route('node', '/*path')

    config.scan('.')
