from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def includeme(config):
    config.include('.error')

    config.include('.admin', route_prefix='/admin')

    config.add_route('index', '/')

    config.add_route('launch', '/launch')
    config.add_route('contact', '/contact')
    config.add_route('about', '/about')
    config.add_route('security', '/security')
    config.add_route('styleguide', '/styleguide')
    config.add_route('subscribe', '/subscribe')
    config.add_route('providers', '/providers')

    config.add_route('questions', '/questions')
    # XXX Include these?
    # config.add_route('how', '/how-it-works')
    # config.add_route('logistics', '/logistics')
    # config.add_route('funding', '/funding')
    # config.add_route('campaign_information', '/campaign-information')
    # config.add_route('user_experience', '/user-experience')

    config.add_route('cart', '/cart')
    config.add_route('cart:add', '/cart/add')

    config.add_route('browse', '/browse')
    config.add_route('search', '/search')
    config.add_route('prelaunch', '/prelaunch')
    config.add_route('crowdfunding', '/crowdfunding')
    config.add_route('preorder', '/preorder')
    config.add_route('instock', '/instock')

    config.include('.browse')
    config.include('.search')

    config.add_route('creators', '/creators')

    config.add_route('ask_question', '/ask-question/{id}')
    # XXX Possibly replaced by suffix on project renderer
    # config.add_route('remind_me', '/remind-me/{id}')

    # User scaffolding routes
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('forgot-password', '/forgot-password')
    config.add_route('forgot-reset', '/forgot-reset')
    config.add_route('account', '/account')

    # This needs to stay the last route registered.
    config.add_route('node', '/*path')

    config.scan('.')
