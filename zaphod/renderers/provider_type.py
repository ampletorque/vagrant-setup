from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyramid.renderers import render

from .. import model


def provider_type_renderer(node, system):
    request = system['request']

    provider_type = node
    providers = model.Session.query(model.Provider).\
        filter(model.Provider.types.contains(provider_type)).\
        filter(model.Provider.published == True).\
        order_by(model.Provider.name).\
        all()

    vars = dict(
        provider_type=provider_type,
        providers=providers,
    )
    return render('provider_type.html', vars, request)


def includeme(config):
    config.add_node_renderer(provider_type_renderer, model.ProviderType)
