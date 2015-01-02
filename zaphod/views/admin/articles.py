from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from formencode import Schema, NestedVariables, validators

from pyramid_uniform import Form, FormRenderer

from ... import model


class UpdateForm(Schema):
    "Schema for validating article update form."
    pre_validators = [NestedVariables()]
    name = validators.UnicodeString(max=255, not_empty=True)
    body = validators.UnicodeString()
    loaded_time = validators.Number(not_empty=True)
    listed = validators.Bool()
    published = validators.Bool()
    use_custom_paths = validators.Bool()
    teaser = validators.UnicodeString(max=255)


class ArticlesView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:articles', renderer='admin/articles.html',
                 permission='authenticated')
    def index(self):
        q = model.Session.query(model.Article)
        return dict(articles=q.all())

    @view_config(route_name='admin:article', renderer='admin/article.html',
                 permission='authenticated')
    def edit(self):
        request = self.request
        article = model.Article.get(request.matchdict['id'])

        form = Form(request, schema=UpdateForm)
        if form.validate():
            # XXX do shit
            pass

        return dict(article=article, renderer=FormRenderer(form))
