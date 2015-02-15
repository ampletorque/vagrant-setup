from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from formencode import Schema, NestedVariables, validators
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, view_defaults

from pyramid_uniform import Form, FormRenderer

from ... import model, custom_validators
from ...helpers.paginate import Page


@view_defaults(route_name='admin:base_edit', renderer='admin/base_edit.html')
class BaseEditView(object):
    def __init__(self, request):
        self.request = request

    def _get_object(self):
        request = self.request
        obj = self.cls.get(request.matchdict['id'])
        if not obj:
            raise HTTPNotFound
        return obj

    @view_config(permission='authenticated')
    def edit(self):
        request = self.request
        obj = self._get_object()

        form = Form(request, schema=self.UpdateForm)
        if form.validate():
            form.bind(obj)
            request.flash('Saved changes.', 'success')
            return HTTPFound(location=request.current_route_url())

        return dict(obj=obj, renderer=FormRenderer(form))


@view_defaults(route_name='admin:base_list', renderer='admin/base_list.html')
class BaseListView(object):
    paginate = False

    def __init__(self, request):
        self.request = request

    @view_config(permission='authenticated')
    def index(self):
        request = self.request

        q = model.Session.query(self.cls)
        if self.paginate:
            final_q = q.order_by(self.cls.id.desc())
            item_count = final_q.count()

            page = Page(request, final_q,
                        page=int(request.params.get('page', 1)),
                        items_per_page=20,
                        item_count=item_count)

            return dict(page=page)
        else:
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
