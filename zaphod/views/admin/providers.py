from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import ForEach, validators

from ... import model

from ...admin import (NodeListView, NodeEditView, NodeUpdateForm,
                      NodeCreateView, NodeDeleteView)


@view_defaults(route_name='admin:provider', renderer='admin/provider.html',
               permission='admin')
@lift()
class ProviderEditView(NodeEditView):
    cls = model.Provider

    class UpdateForm(NodeUpdateForm):
        provider_type_ids = ForEach(validators.Int)

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
