from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_uniform import Form, FormRenderer
from formencode import Schema, validators

from ... import model


class EditForm(Schema):
    allow_extra_fields = False
    name = validators.UnicodeString(not_empty=True)
    email = validators.Email(not_empty=True)


class UsersView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:users', renderer='admin/users.html',
                 permission='authenticated')
    def index(self):
        q = model.Session.query(model.User)
        return dict(users=q.all())

    @view_config(route_name='admin:user', renderer='admin/user.html',
                 permission='authenticated')
    def edit(self):
        request = self.request
        user = model.User.get(request.matchdict['id'])

        form = Form(request, schema=EditForm)
        if form.validate():
            form.bind(user)
            request.flash("Saved changes.", 'success')
            return HTTPFound(location=request.route_url('admin:user',
                                                        id=user.id))

        return dict(user=user, renderer=FormRenderer(form))
