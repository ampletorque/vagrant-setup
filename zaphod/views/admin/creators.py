from pyramid.view import view_defaults
from formencode import validators
from venusian import lift

from ... import model

from ...admin import (NodeEditView, NodeListView, NodeUpdateForm,
                      NodeCreateView)


@view_defaults(route_name='admin:creator', renderer='admin/creator.html',
               permission='admin')
@lift()
class CreatorEditView(NodeEditView):
    cls = model.Creator

    class UpdateForm(NodeUpdateForm):
        home_url = validators.URL(max=255)
        location = validators.UnicodeString(max=255)


@view_defaults(route_name='admin:creators', renderer='admin/creators.html',
               permission='admin')
@lift()
class CreatorListView(NodeListView):
    cls = model.Creator


@view_defaults(route_name='admin:creators:new',
               renderer='admin/creators_new.html', permission='admin')
@lift()
class CreateCreateView(NodeCreateView):
    cls = model.Creator
    obj_route_name = 'admin:creator'
