from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def includeme(config):
    # XXX These have to exist...
    config.add_route('admin:base_edit', '/base-edit')
    config.add_route('admin:base_list', '/base-list')

    config.add_route('admin:dashboard', '/dashboard')

    config.add_route('admin:creators', '/creators')
    config.add_route('admin:creator', '/creator/{id}')

    config.add_route('admin:projects', '/projects')
    config.add_route('admin:project', '/project/{id}')

    config.add_route('admin:users', '/users')
    config.add_route('admin:user', '/user/{id}')

    config.add_route('admin:articles', '/articles')
    config.add_route('admin:article', '/article/{id}')

    config.add_route('admin:orders', '/orders')
    config.add_route('admin:order', '/order/{id}')
    config.add_route('admin:order-resend', '/order/{id}/resend')

    config.add_route('admin:vendor_orders', '/vendor-orders')
    config.add_route('admin:vendor_order', '/vendor-order/{id}')

    config.add_route('admin:images', '/images')
    config.add_route('admin:image', '/image/{id}')

    config.add_route('admin:provider_types', '/provider-types')
    config.add_route('admin:provider_type', '/provider-type/{id}')

    config.add_route('admin:providers', '/providers')
    config.add_route('admin:provider', '/provider/{id}')

    config.add_route('admin:tags', '/tags')
    config.add_route('admin:tag', '/tag/{id}')

    config.add_route('admin:leads', '/leads')
    config.add_route('admin:lead', '/lead/{id}')

    config.add_route('admin:settings', '/settings')

    config.add_route('admin:mail_template', '/mail-template/{template_name}')

    config.add_route('admin:reports', '/reports')
    config.add_route('admin:markdown_guide', '/markdown-guide')
