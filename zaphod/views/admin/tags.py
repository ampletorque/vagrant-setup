from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from formencode import Schema, NestedVariables, validators

from pyramid_uniform import Form, FormRenderer

from ... import model


class UpdateForm(Schema):
    "Schema for validating tag update form."
    pre_validators = [NestedVariables()]
    name = validators.UnicodeString(max=255, not_empty=True)
    body = validators.UnicodeString()
    loaded_time = validators.Number(not_empty=True)
    listed = validators.Bool()
    published = validators.Bool()
    use_custom_paths = validators.Bool()
    teaser = validators.UnicodeString(max=255)


class TagsView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:tags', renderer='admin/tags.html',
                 permission='authenticated')
    def index(self):
        q = model.Session.query(model.Tag)
        return dict(tags=q.all())

    @view_config(route_name='admin:tag', renderer='admin/tag.html',
                 permission='authenticated')
    def edit(self):
        request = self.request
        tag = model.Tag.get(request.matchdict['id'])

        form = Form(request, schema=UpdateForm)
        if form.validate():
            # XXX do shit
            pass

        return dict(tag=tag, renderer=FormRenderer(form))
