from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift

from ... import model

from .base import NodeEditView, NodeListView, NodeUpdateForm


@view_defaults(route_name='admin:creator', renderer='admin/creator.html')
@lift()
class CreatorEditView(NodeEditView):
    cls = model.Creator

    UpdateForm = NodeUpdateForm


@view_defaults(route_name='admin:creators', renderer='admin/creators.html')
@lift()
class CreatorListView(NodeListView):
    cls = model.Creator
