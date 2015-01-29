from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.compat import string_types


def add_node_view(config, view, cls, suffix=None, renderer=None):
    suffix = tuple(suffix) if suffix else None
    def register():
        lookup = config.registry.setdefault('node_views', {})
        lookup[cls, suffix] = view, renderer
    config.action(('node_view', cls, suffix), register)


def lookup_node_view(registry, cls, suffix):
    views = registry['node_views']
    while cls is not None:
        if (cls, suffix) in views:
            return views[cls, suffix]
        cls = cls.__base__


def htmlstring_renderer_factory(info):
    def _render(value, system):
        if not isinstance(value, string_types):
            value = str(value)
        request = system.get('request')
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = b'text/html'
        return value
    return _render


def includeme(config):
    config.add_renderer(name='htmlstring', factory=htmlstring_renderer_factory)
    config.add_directive('add_node_view', add_node_view)
