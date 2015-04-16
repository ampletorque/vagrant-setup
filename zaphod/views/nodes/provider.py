from pyramid.view import view_config

from ... import model

from . import NodePredicate


@view_config(route_name='node', renderer='provider.html',
             custom_predicates=[NodePredicate(model.Provider)])
def provider_view(context, request):
    provider = context.node
    return dict(provider=provider)
