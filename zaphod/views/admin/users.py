from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, validators

from ... import model, custom_validators

from .base import BaseEditView, BaseListView, BaseCreateView


@view_defaults(route_name='admin:user', renderer='admin/user.html')
@lift()
class UserEditView(BaseEditView):
    cls = model.User

    class UpdateForm(Schema):
        allow_extra_fields = False
        name = validators.UnicodeString(not_empty=True)
        email = validators.Email(not_empty=True)
        password = validators.UnicodeString()
        password2 = validators.UnicodeString()
        enabled = validators.Bool()
        admin = validators.Bool()
        show_admin_bars = validators.Bool()
        show_location = validators.Bool()
        show_in_backers = validators.Bool()
        show_name = validators.Bool()
        timezone = validators.String()
        url_path = custom_validators.URLString()
        twitter_username = custom_validators.TwitterUsername()
        chained_validators = [validators.FieldsMatch('password', 'password2')]
        new_comment = custom_validators.CommentBody()


@view_defaults(route_name='admin:users', renderer='admin/users.html')
@lift()
class UserListView(BaseListView):
    cls = model.User
    paginate = True


@view_defaults(route_name='admin:users:new',
               renderer='admin/users_new.html')
@lift()
class UserCreateView(BaseCreateView):
    cls = model.User
    obj_route_name = 'admin:user'

    class CreateForm(Schema):
        allow_extra_fields = False
        name = validators.UnicodeString(not_empty=True)
