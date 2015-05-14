from pyramid.view import view_defaults
from venusian import lift
from formencode import ForEach, validators

from ... import model, custom_validators

from ...admin import (NodeListView, NodeEditView, NodeUpdateForm,
                      NodeCreateView, NodeDeleteView)


@view_defaults(route_name='admin:provider', renderer='admin/provider.html',
               permission='admin')
@lift()
class ProviderEditView(NodeEditView):
    cls = model.Provider

    class UpdateForm(NodeUpdateForm):
        provider_type_ids = ForEach(validators.Int)
        email = validators.Email(not_empty=False)
        home_url = validators.URL(max=255)
        mailing = custom_validators.AddressSchema

        lat = validators.Number()
        lon = validators.Number()

    def _update_object(self, form, obj):
        obj.types.clear()
        for provider_type_id in form.data.pop('provider_type_ids'):
            obj.types.add(model.ProviderType.get(provider_type_id))

        NodeEditView._update_object(self, form, obj)


@view_defaults(route_name='admin:providers', renderer='admin/providers.html',
               permission='admin')
@lift()
class ProviderListView(NodeListView):
    cls = model.Provider


@view_defaults(route_name='admin:providers:new',
               renderer='admin/providers_new.html', permission='admin')
@lift()
class ProviderCreateView(NodeCreateView):
    cls = model.Provider
    obj_route_name = 'admin:provider'


@view_defaults(route_name='admin:provider:delete', permission='admin')
@lift()
class ProviderDeleteView(NodeDeleteView):
    cls = model.Provider
    list_route_name = 'admin:providers'
