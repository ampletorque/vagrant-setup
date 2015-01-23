from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift

from ... import model

from .base import NodeEditView, NodeListView, NodeUpdateForm


@view_defaults(route_name='admin:tag', renderer='admin/tag.html')
@lift()
class TagEditView(NodeEditView):
    cls = model.Tag

    UpdateForm = NodeUpdateForm


@view_defaults(route_name='admin:tags', renderer='admin/tags.html')
@lift()
class TagListView(NodeListView):
    cls = model.Tag
