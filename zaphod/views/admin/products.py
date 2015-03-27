from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime, time

from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from venusian import lift
from formencode import Schema, NestedVariables, ForEach, validators

from pyramid_uniform import Form, FormRenderer, crud_update

from ... import model

from ...admin import BaseEditView


class OptionValueSchema(Schema):
    allow_extra_fields = False
    id = validators.String(not_empty=True)
    description = validators.UnicodeString(not_empty=True)
    price_increase = validators.Number(if_empty=0.0)
    gravity = validators.Int(not_empty=True)
    published = validators.Bool()


class OptionSchema(Schema):
    allow_extra_fields = False
    id = validators.String(not_empty=True)
    name = validators.UnicodeString(not_empty=True)
    gravity = validators.Int(not_empty=True)
    default_value_id = validators.String(if_missing=0)
    published = validators.Bool()
    values = ForEach(OptionValueSchema)


class OptionsForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    options = ForEach(OptionSchema)


class BatchSchema(Schema):
    allow_extra_fields = False
    id = validators.String(not_empty=True)
    qty = validators.Int(not_empty=False)
    orig_qty_claimed = validators.Int(not_empty=False)
    ship_time = validators.DateConverter(month_style='yyyy/mm/dd')


class ScheduleForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    batches = ForEach(BatchSchema)


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

    def _update_schedule(self, form, product):
        batches = form.data['batches']
        batches_remaining = set(product.batches)
        for ii, batch_params in enumerate(batches):
            batch_id = batch_params['id']
            new_ship_time = datetime.combine(batch_params['ship_time'], time())
            if batch_id.startswith('new'):
                batch = model.Batch(ship_time=new_ship_time)
                product.batches.append(batch)
            else:
                batch = model.Batch.get(batch_id)
                batch.ship_time = new_ship_time
                batches_remaining.remove(batch)
            assert batch.product == product
            assert batch.qty_claimed == batch_params['orig_qty_claimed'], \
                "qty claimed changed while editing"
            new_qty = batch_params['qty']
            if new_qty is None:
                assert (ii + 1) == len(batches), \
                    "infinite qty can only be last batch"
            else:
                assert new_qty > batch.qty_claimed, \
                    "new batch qty must be greater than already claimed"
            batch.qty = new_qty

        for batch in batches_remaining:
            assert batch.qty_claimed == 0, \
                "can't delete batch that has been allocated"
            model.Session.delete(batch)

        model.Session.flush()
        product.validate_schedule()

        self._touch_obj(product)
        self.request.theme.invalidate_project(product.project.id)
        self.request.flash("Saved options.", 'success')

    @view_config(route_name='admin:product:schedule',
                 renderer='admin/product_schedule.html')
    def schedule(self):
        request = self.request
        product = self._get_object()

        form = Form(request, ScheduleForm)
        if form.validate():
            self._update_schedule(form, product)
            request.flash("Saved schedule.", 'success')
            return HTTPFound(location=request.current_route_url())

        return {
            'obj': product,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:product:schedule', request_method='POST',
                 xhr=True, renderer='json')
    def schedule_ajax(self):
        request = self.request
        product = self._get_object()

        form = Form(request, ScheduleForm)
        if form.validate():
            self._update_schedule(form, product)
            return {
                'status': 'ok',
                'location': request.current_route_url(),
            }
        else:
            return {
                'status': 'fail',
                'errors': form.errors,
            }

    def _update_option_values(self, option_params, option):
        values_remaining = set(option.values)
        for value_params in option_params.pop('values'):
            value_id = value_params.pop('id')
            if value_id.startswith('new'):
                value = model.OptionValue()
                option.values.append(value)
            else:
                value = model.OptionValue.get(value_id)
                values_remaining.remove(value)
            assert value.option == option
            crud_update(value, value_params)
            if option_params['default_value_id'] == value_id:
                value.is_default = True
            else:
                value.is_default = None
        # XXX
        assert not values_remaining, \
            "didn't get values %r" % values_remaining

    def _update_options(self, form, product):
        options_remaining = set(product.options)
        for option_params in form.data['options']:
            option_id = option_params.pop('id')
            if option_id.startswith('new'):
                option = model.Option()
                product.options.append(option)
                is_new = True
            else:
                option = model.Option.get(option_id)
                options_remaining.remove(option)
                is_new = False
            for value in option.values:
                value.is_default = None
            assert option.product == product
            self._update_option_values(option_params, option)
            crud_update(option, option_params)
            model.Session.flush()
            if is_new:
                for sku in product.skus:
                    sku.option_values.add(option.default_value)
        # XXX
        assert not options_remaining, \
            "didn't get options %r" % options_remaining
        self._touch_obj(product)
        self.request.theme.invalidate_project(product.project.id)
        self.request.flash("Saved options.", 'success')

    @view_config(route_name='admin:product:options',
                 renderer='admin/product_options.html')
    def options(self):
        request = self.request
        product = self._get_object()

        form = Form(request, OptionsForm)
        if form.validate():
            self._update_options(form, product)
            return HTTPFound(location=request.current_route_url())

        return {
            'obj': product,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:product:options', request_method='POST',
                 xhr=True, renderer='json')
    def options_ajax(self):
        request = self.request
        product = self._get_object()

        form = Form(request, OptionsForm)
        if form.validate():
            self._update_options(form, product)
            return {
                'status': 'ok',
                'location': request.current_route_url(),
            }
        else:
            return {
                'status': 'fail',
                'errors': form.errors,
            }

    @view_config(route_name='admin:product:skus',
                 renderer='admin/product_skus.html')
    def skus(self):
        product = self._get_object()
        return {'obj': product}
