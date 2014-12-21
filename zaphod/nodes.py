from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


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


def includeme(config):
    config.add_directive('add_node_renderer', add_node_renderer)
