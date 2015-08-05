from pyramid.view import view_defaults, view_config
from venusian import lift

from ... import model

from ...admin import (NodeEditView, NodeListView, NodeUpdateForm,
                      NodeCreateView, NodeDeleteView)


@view_defaults(route_name='admin:tag', renderer='admin/tag.html',
               permission='admin')
@lift()
class TagEditView(NodeEditView):
    cls = model.Tag

    UpdateForm = NodeUpdateForm


@view_defaults(route_name='admin:tags', renderer='admin/tags.html',
               permission='admin')
@lift()
class TagListView(NodeListView):
    cls = model.Tag

    @view_config(route_name='admin:tags:ajax-list', renderer='json', xhr=True)
    def ajax_list(self):
        q = model.Session.query(model.Tag).order_by(model.Tag.name)
        return {
            'tags': [{'id': tag.id, 'name': tag.name} for tag in q]
        }


@view_defaults(route_name='admin:tags:new',
               renderer='admin/tags_new.html', permission='admin')
@lift()
class TagCreateView(NodeCreateView):
    cls = model.Tag
    obj_route_name = 'admin:tag'


@view_defaults(route_name='admin:tag:delete', permission='admin')
@lift()
class TagDeleteView(NodeDeleteView):
    cls = model.Tag
    list_route_name = 'admin:tags'
