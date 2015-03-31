from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from ... import model

from . import NodePredicate


@view_config(route_name='node', renderer='provider_type.html',
             custom_predicates=[NodePredicate(model.ProviderType)])
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
