from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift

from ... import model

from ...admin import (NodeEditView, NodeListView, NodeUpdateForm,
                      NodeCreateView)


@view_defaults(route_name='admin:creator', renderer='admin/creator.html')
@lift()
class CreatorEditView(NodeEditView):
    cls = model.Creator

    UpdateForm = NodeUpdateForm


@view_defaults(route_name='admin:creators', renderer='admin/creators.html')
@lift()
class CreatorListView(NodeListView):
    cls = model.Creator


@view_defaults(route_name='admin:creators:new',
               renderer='admin/creators_new.html')
@lift()
class CreateCreateView(NodeCreateView):
    cls = model.Creator
    obj_route_name = 'admin:creator'
