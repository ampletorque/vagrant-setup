from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config


@view_config(route_name='admin:help',
             renderer='admin/help/index.html',
             permission='admin')
def index_view(request):
    return {}


@view_config(route_name='admin:help:markdown',
             renderer='admin/help/markdown.html',
             permission='admin')
def markdown_view(request):
    return {}


@view_config(route_name='admin:help:image-tags',
             renderer='admin/help/image_tags.html',
             permission='admin')
def image_tag_view(request):
    return {}
