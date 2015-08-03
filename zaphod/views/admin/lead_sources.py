from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, NestedVariables, validators

from ... import model

from ...admin import BaseListView, BaseEditView, BaseCreateView


@view_defaults(route_name='admin:lead-source', renderer='admin/lead_source.html',
               permission='admin')
@lift()
class LeadSourceEditView(BaseEditView):
    cls = model.LeadSource

    class UpdateForm(Schema):
        "Schema for validating lead source update form."
        allow_extra_fields = False
        pre_validators = [NestedVariables()]
        name = validators.String(not_empty=True)
        category = validators.String()


@view_defaults(route_name='admin:lead-sources', renderer='admin/lead_sources.html',
               permission='admin')
@lift()
class LeadSourceListView(BaseListView):
    cls = model.LeadSource


@view_defaults(route_name='admin:lead-sources:new', renderer='admin/lead_sources_new.html',
               permission='admin')
@lift()
class LeadSourceCreateView(BaseCreateView):
    cls = model.LeadSource
    obj_route_name = 'admin:lead-source'

    class CreateForm(Schema):
        allow_extra_fields = False
        name = validators.String(not_empty=True)
        category = validators.String()
