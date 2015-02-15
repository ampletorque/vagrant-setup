from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift

from ... import model

from .base import NodeEditView


@view_defaults(route_name='admin:update', renderer='admin/update.html')
@lift()
class UpdateEditView(NodeEditView):
    cls = model.ProjectUpdate
