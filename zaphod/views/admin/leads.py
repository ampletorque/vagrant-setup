from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, NestedVariables, validators

from ... import model, custom_validators

from ...admin import BaseListView, BaseEditView, BaseCreateView


@view_defaults(route_name='admin:lead', renderer='admin/lead.html',
               permission='admin')
@lift()
class LeadEditView(BaseEditView):
    cls = model.Lead

    class UpdateForm(Schema):
        "Schema for validating lead update form."
        allow_extra_fields = False
        pre_validators = [NestedVariables()]
        name = validators.String(not_empty=True)
        description = validators.String()
        notes = validators.String()
        discount = validators.String()
        status = validators.String(not_empty=True)
        assigned_to_id = validators.Int()
        source_id = validators.Int()
        new_source = validators.String()
        contact_point = validators.String()
        estimated_launch_time = \
            custom_validators.UTCDateConverter(month_style='yyyy/mm/dd')
        campaign_duration_days = validators.Int()
        person = validators.String(if_empty=u'')
        email = validators.Email(if_empty=u'')
        phone = validators.String(if_empty=u'')
        new_comment = validators.String()

        was_contacted = validators.Bool()
        next_contact_days = validators.Int()


@view_defaults(route_name='admin:leads', renderer='admin/leads.html',
               permission='admin')
@lift()
class LeadListView(BaseListView):
    cls = model.Lead


@view_defaults(route_name='admin:leads:new', renderer='admin/leads_new.html',
               permission='admin')
@lift()
class LeadCreateView(BaseCreateView):
    cls = model.Lead
    obj_route_name = 'admin:lead'

    class CreateForm(Schema):
        allow_extra_fields = False
        name = validators.String(not_empty=True)
        source_id = validators.Int()
        new_source = validators.String()
