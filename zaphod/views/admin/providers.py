from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift

from ... import model

from .base import NodeListView, NodeEditView, NodeUpdateForm


@view_defaults(route_name='admin:provider', renderer='admin/provider.html')
@lift()
class ProviderEditView(NodeEditView):
    cls = model.Provider

    UpdateForm = NodeUpdateForm


@view_defaults(route_name='admin:providers', renderer='admin/providers.html')
@lift()
class ProviderListView(NodeListView):
    cls = model.Provider
