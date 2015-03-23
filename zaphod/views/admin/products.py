from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from venusian import lift
from formencode import Schema, NestedVariables, ForEach, validators

from pyramid_uniform import Form, FormRenderer

from ... import model

from ...admin import BaseEditView


class ScheduleForm(Schema):
    allow_extra_fields = False


class OptionValueSchema(Schema):
    allow_extra_fields = False
    description = validators.UnicodeString()
    price_increase = validators.Number(if_empty=0.0)
    published = validators.Bool()


class OptionSchema(Schema):
    allow_extra_fields = False
    name = validators.UnicodeString()
    gravity = validators.Int(not_empty=True)
    default_value_id = validators.Int(if_missing=0)
    published = validators.Bool()
    values = ForEach(OptionValueSchema)


class OptionsForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    options = ForEach(OptionSchema)


@view_defaults(route_name='admin:product', renderer='admin/product.html',
               permission='admin')
@lift()
class ProductEditView(BaseEditView):
    cls = model.Product

    class UpdateForm(Schema):
        allow_extra_fields = False
        name = validators.UnicodeString(not_empty=True)
        international_available = validators.Bool()
        international_surcharge = validators.Number()
        gravity = validators.Int()
        non_physical = validators.Bool()
        published = validators.Bool()
        price = validators.Number()
        accepts_preorders = validators.Bool()

    def _update_obj(self, form, obj):
        BaseEditView._update_obj(self, form, obj)
        self.request.theme.invalidate_project(obj.project.id)

    @view_config(route_name='admin:product:schedule',
                 renderer='admin/product_schedule.html')
    def schedule(self):
        request = self.request
        product = self._get_object()

        form = Form(request, ScheduleForm)
        if form.validate():
            # XXX
            request.flash("Saved schedule.", 'success')
            return HTTPFound(location=request.current_route_url())

        return {
            'obj': product,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:product:options',
                 renderer='admin/product_options.html')
    def options(self):
        request = self.request
        product = self._get_object()

        form = Form(request, OptionsForm)
        if form.validate():
            # XXX
            request.flash("Saved options.", 'success')
            return HTTPFound(location=request.current_route_url())

        return {
            'obj': product,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:product:skus',
                 renderer='admin/product_skus.html')
    def skus(self):
        product = self._get_object()
        return {'obj': product}
