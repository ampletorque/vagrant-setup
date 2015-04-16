from pyramid.view import view_config

from .. import model


@view_config(route_name='providers', renderer='providers.html')
def providers_view(request):
    provider_types = model.Session.query(model.ProviderType).\
        filter(model.ProviderType.published == True).\
        order_by(model.ProviderType.name)

    providers = model.Session.query(model.Provider).\
        filter(model.Provider.published == True).\
        order_by(model.Provider.id.desc()).\
        limit(5)

    return {'provider_types': provider_types,
            'providers': providers}
