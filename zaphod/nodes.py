from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


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


def includeme(config):
    config.add_directive('add_node_view', add_node_view)
