from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import validators

from ... import model

from .base import NodeEditView, NodeListView, NodeUpdateForm


@view_defaults(route_name='admin:project', renderer='admin/project.html')
@lift()
class ProjectEditView(NodeEditView):
    cls = model.Project

    class UpdateForm(NodeUpdateForm):
        "Schema for validating project update form."
        prelaunch_vimeo_id = validators.Int()
        prelaunch_teaser = validators.UnicodeString()
        prelaunch_body = validators.UnicodeString()

        crowdfunding_vimeo_id = validators.Int()
        # Crowdfunding teaser and body are handled by the base node schema

        available_vimeo_id = validators.Int()
        available_teaser = validators.UnicodeString()
        available_body = validators.UnicodeString()

        target = validators.Number()
        start_time = validators.DateConverter()
        # Remember we probably want to add a day to this value.
        end_time = validators.DateConverter()
        gravity = validators.Int(not_empty=True)

    @view_config(route_name='admin:project:products',
                 renderer='admin/project_products.html')
    def products(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:owners',
                 renderer='admin/project_owners.html')
    def owners(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:updates',
                 renderer='admin/project_updates.html')
    def updates(self):
        project = self._get_object()
        return {'obj': project}


@view_defaults(route_name='admin:projects', renderer='admin/projects.html')
@lift()
class ProjectListView(NodeListView):
    cls = model.Project
