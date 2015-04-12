from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, validators

from ... import model

from ...admin import BaseEditView


@view_defaults(route_name='admin:transfer', renderer='admin/transfer.html',
               permission='admin')
@lift()
class TransferEditView(BaseEditView):
    cls = model.ProjectTransfer

    class UpdateForm(Schema):
        allow_extra_fields = False
        amount = validators.Number(not_empty=True)
        fee = validators.Number(if_empty=0)
        method = validators.String(not_empty=True)
        reference = validators.UnicodeString()
