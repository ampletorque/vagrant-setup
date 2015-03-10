from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, validators

from ... import model

from .base import BaseEditView


@view_defaults(route_name='admin:product', renderer='admin/product.html')
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
