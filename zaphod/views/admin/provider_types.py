from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift

from ... import model

from .base import NodeEditView, NodeListView, NodeUpdateForm


@view_defaults(route_name='admin:provider_type',
               renderer='admin/provider_type.html')
@lift()
class ProviderTypeEditView(NodeEditView):
    cls = model.ProviderType

    UpdateForm = NodeUpdateForm


@view_defaults(route_name='admin:provider_types',
               renderer='admin/provider_types.html')
@lift()
class ProviderTypeListView(NodeListView):
    cls = model.ProviderType
