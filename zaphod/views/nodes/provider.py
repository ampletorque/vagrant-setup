from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ... import model

from . import NodePredicate


def provider_view(context, request):
    provider = context.node
    return dict(provider=provider)


def includeme(config):
    config.add_view(provider_view,
                    route_name='node',
                    custom_predicates=[NodePredicate(model.Provider)],
                    renderer='provider.html')
