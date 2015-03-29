from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ... import model

from . import NodePredicate


def provider_type_view(context, request):
    provider_type = context.node
    providers = model.Session.query(model.Provider).\
        filter(model.Provider.types.contains(provider_type)).\
        filter(model.Provider.published == True).\
        order_by(model.Provider.name).\
        all()

    return dict(
        provider_type=provider_type,
        providers=providers,
    )


def includeme(config):
    config.add_view(provider_type_view,
                    route_name='node',
                    custom_predicates=[NodePredicate(model.ProviderType)],
                    renderer='provider_type.html')
