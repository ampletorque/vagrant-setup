from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ... import model


def provider_view(provider, system):
    return dict(provider=provider)


def includeme(config):
    config.add_node_view(provider_view, model.Provider,
                         renderer='provider.html')
