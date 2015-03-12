from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift

from ... import model

from ...editing import NodeEditView


@view_defaults(route_name='admin:update', renderer='admin/update.html')
@lift()
class UpdateEditView(NodeEditView):
    cls = model.ProjectUpdate

    def _update_obj(self, form, obj):
        NodeEditView._update_obj(self, form, obj)
        self.request.theme.invalidate_project(obj.project.id)
