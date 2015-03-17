from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift

from ... import model

from ...admin import (NodeEditView, NodeListView, NodeUpdateForm,
                      NodeCreateView)


@view_defaults(route_name='admin:provider-type',
               renderer='admin/provider_type.html', permission='admin')
@lift()
class ProviderTypeEditView(NodeEditView):
    cls = model.ProviderType

    UpdateForm = NodeUpdateForm


@view_defaults(route_name='admin:provider-types',
               renderer='admin/provider_types.html', permission='admin')
@lift()
class ProviderTypeListView(NodeListView):
    cls = model.ProviderType


@view_defaults(route_name='admin:provider-types:new',
               renderer='admin/provider_types_new.html', permission='admin')
@lift()
class ProviderTypeCreateView(NodeCreateView):
    cls = model.ProviderType
    obj_route_name = 'admin:provider-type'
