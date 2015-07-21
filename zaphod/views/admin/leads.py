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
        new_comment = custom_validators.CommentBody()

        description = validators.UnicodeString()
        contact = validators.UnicodeString()

        assigned_to_id = validators.Int()

        dead_reason = validators.String()

        source_id = validators.Int(not_empty=True)
        is_inbound = validators.Bool()
        contact_channel = validators.String()

        initial_est_launch_time = validators.DateConverter(month_style='yyyy/mm/dd')
        initial_est_tier = validators.String()
        initial_est_six_month_sales = validators.Int(not_empty=True)
        initial_est_six_month_percentage = validators.Int(not_empty=True)

        refined_est_launch_time = validators.DateConverter(month_style='yyyy/mm/dd')
        refined_est_tier = validators.String()
        refined_est_six_month_sales = validators.Int(not_empty=True)
        refined_est_six_month_percentage = validators.Int(not_empty=True)


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
