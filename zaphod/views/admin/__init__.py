from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def includeme(config):
    # XXX These have to exist...
    config.add_route('admin:base_edit', '/base-edit')
    config.add_route('admin:base_list', '/base-list')
    config.add_route('admin:base_create', '/base-create')

    config.add_route('admin:dashboard', '/dashboard')

    config.add_route('admin:creators', '/creators')
    config.add_route('admin:creators:new', '/creators/new')
    config.add_route('admin:creator', '/creator/{id}')

    config.add_route('admin:projects', '/projects')
    config.add_route('admin:projects:new', '/projects/new')

    config.add_route('admin:project', '/project/{id}')
    config.add_route('admin:project:products', '/project/{id}/products')
    config.add_route('admin:project:products:new',
                     '/project/{id}/products/new')

    config.add_route('admin:project:owners', '/project/{id}/owners')
    config.add_route('admin:project:owners:new', '/project/{id}/owners/new')
    config.add_route('admin:project:updates', '/project/{id}/updates')
    config.add_route('admin:project:updates:new', '/project/{id}/updates/new')
    config.add_route('admin:project:emails', '/project/{id}/emails')
    config.add_route('admin:project:ship', '/project/{id}/ship')

    config.add_route('admin:project:reports', '/project/{id}/reports')
    config.add_route('admin:project:reports:funding', '/project/{id}/funding')
    config.add_route('admin:project:reports:status', '/project/{id}/status')
    config.add_route('admin:project:reports:balance', '/project/{id}/balance')
    config.add_route('admin:project:reports:skus', '/project/{id}/skus')

    config.add_route('admin:product', '/product/{id}')
    config.add_route('admin:update', '/update/{id}')

    config.add_route('admin:users', '/users')
    config.add_route('admin:users:new', '/users/new')
    config.add_route('admin:user', '/user/{id}')

    config.add_route('admin:articles', '/articles')
    config.add_route('admin:articles:new', '/articles/new')
    config.add_route('admin:article', '/article/{id}')

    config.add_route('admin:orders', '/orders')
    config.add_route('admin:orders:new', '/orders/new')
    config.add_route('admin:order', '/order/{id}')
    config.add_route('admin:order:resend', '/order/{id}/resend')
    config.add_route('admin:order:print', '/order/{id}/print')
    config.add_route('admin:order:cancel', '/order/{id}/cancel')
    config.add_route('admin:order:hold', '/order/{id}/hold')
    config.add_route('admin:order:address', '/order/{id}/address')
    config.add_route('admin:order:user', '/order/{id}/user')
    config.add_route('admin:order:payment', '/order/{id}/payment')
    config.add_route('admin:order:refund', '/order/{id}/refund')

    config.add_route('admin:vendor_orders', '/vendor-orders')
    config.add_route('admin:vendor_orders:new', '/vendor-orders/new')
    config.add_route('admin:vendor_order', '/vendor-order/{id}')
    config.add_route('admin:vendor_order:mark-sent',
                     '/vendor-order/{id}/mark-sent')
    config.add_route('admin:vendor_order:mark-confirmed',
                     '/vendor-order/{id}/mark-confirmed')
    config.add_route('admin:vendor_order:receive-invoice',
                     '/vendor-order/{id}/receive-invoice')
    config.add_route('admin:vendor_order:receive-shipment',
                     '/vendor-order/{id}/receive-shipment')

    config.add_route('admin:vendor_shipment', '/vendor-shipment/{id}')
    config.add_route('admin:vendor_invoice', '/vendor-invoice/{id}')

    config.add_route('admin:images', '/images')
    config.add_route('admin:images:upload', '/images/upload')
    config.add_route('admin:image', '/image/{id}')

    config.add_route('admin:provider_types', '/provider-types')
    config.add_route('admin:provider_types:new', '/provider-types/new')
    config.add_route('admin:provider_type', '/provider-type/{id}')

    config.add_route('admin:providers', '/providers')
    config.add_route('admin:providers:new', '/providers/new')
    config.add_route('admin:provider', '/provider/{id}')

    config.add_route('admin:tags', '/tags')
    config.add_route('admin:tags:new', '/tags/new')
    config.add_route('admin:tag', '/tag/{id}')

    config.add_route('admin:leads', '/leads')
    config.add_route('admin:leads:new', '/leads/new')
    config.add_route('admin:lead', '/lead/{id}')

    config.add_route('admin:settings', '/settings')

    config.add_route('admin:mail_template', '/mail-template/{template_name}')

    config.add_route('admin:help', '/help')
    config.add_route('admin:help:markdown', '/help/markdown')
    config.add_route('admin:help:image-tags', '/help/image-tags')

    config.include('.reports', route_prefix='/reports')
