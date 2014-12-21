from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.compat import string_types


def add_node_renderer(config, f, cls, accept_suffix=False):
    def register():
        lookup = config.registry.setdefault('node_renderers', {})
        lookup[cls] = (f, accept_suffix)
    config.action(('node_renderer', cls), register)


def lookup_node_renderer(registry, cls):
    renderers = registry['node_renderers']
    while cls is not None:
        if cls in renderers:
            return renderers[cls]
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
    config.add_directive('add_node_renderer', add_node_renderer)
