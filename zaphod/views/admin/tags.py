from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift

from ... import model

from ...admin import (NodeEditView, NodeListView, NodeUpdateForm,
                      NodeCreateView)


@view_defaults(route_name='admin:tag', renderer='admin/tag.html')
@lift()
class TagEditView(NodeEditView):
    cls = model.Tag

    UpdateForm = NodeUpdateForm


@view_defaults(route_name='admin:tags', renderer='admin/tags.html')
@lift()
class TagListView(NodeListView):
    cls = model.Tag


@view_defaults(route_name='admin:tags:new',
               renderer='admin/tags_new.html')
@lift()
class TagCreateView(NodeCreateView):
    cls = model.Tag
    obj_route_name = 'admin:tag'
