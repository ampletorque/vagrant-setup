from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, validators

from ... import model

from .base import BaseEditView, BaseListView


@view_defaults(route_name='admin:user', renderer='admin/user.html')
@lift()
class UserEditView(BaseEditView):
    cls = model.User

    class UpdateForm(Schema):
        allow_extra_fields = False
        name = validators.UnicodeString(not_empty=True)
        email = validators.Email(not_empty=True)


@view_defaults(route_name='admin:users', renderer='admin/users.html')
@lift()
class UserListView(BaseListView):
    cls = model.User
