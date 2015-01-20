from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from formencode import Schema, NestedVariables, validators
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config, view_defaults

from pyramid_uniform import Form, FormRenderer

from ... import model, custom_validators


@view_defaults(route_name='admin:base_edit', renderer='admin/base_edit.html')
class BaseEditView(object):
    def __init__(self, request):
        self.request = request

    @view_config(permission='authenticated')
    def edit(self):
        request = self.request
        obj = self.cls.get(request.matchdict['id'])

        form = Form(request, schema=self.UpdateForm)
        if form.validate():
            form.bind(obj)
            request.flash('Saved changes.', 'success')
            return HTTPFound(location=request.current_route_url())

        return dict(obj=obj, renderer=FormRenderer(form))


@view_defaults(route_name='admin:base_list', renderer='admin/base_list.html')
class BaseListView(object):
    def __init__(self, request):
        self.request = request

    @view_config(permission='authenticated')
    def index(self):
        q = model.Session.query(self.cls)
        return dict(objs=q.all())


class NodeUpdateForm(Schema):
    pre_validators = [NestedVariables()]

    name = validators.UnicodeString(max=255, not_empty=True)
    override_path = custom_validators.URLString(if_missing=None)

    keywords = validators.UnicodeString()
    teaser = validators.UnicodeString()
    body = validators.UnicodeString()

    listed = validators.Bool()
    published = validators.Bool()


class NodeEditView(BaseEditView):
    pass


class NodeListView(BaseListView):
    pass
