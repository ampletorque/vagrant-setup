from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from formencode import Schema, NestedVariables, validators

from pyramid_uniform import Form, FormRenderer

from ... import model, custom_validators


class UpdateForm(Schema):
    "Schema for validating article update form."
    pre_validators = [NestedVariables()]

    name = validators.UnicodeString(max=255, not_empty=True)
    use_custom_paths = validators.Bool()
    override_path = custom_validators.URLString(if_missing=None)

    keywords = validators.UnicodeString()
    teaser = validators.UnicodeString()
    body = validators.UnicodeString()

    category = validators.UnicodeString(max=255)

    show_heading = validators.Bool()
    show_article_list = validators.Bool()
    listed = validators.Bool()
    published = validators.Bool()


class ArticleEditView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:article', renderer='admin/article.html',
                 permission='authenticated')
    def edit(self):
        request = self.request
        article = model.Article.get(request.matchdict['id'])

        form = Form(request, schema=UpdateForm)
        if form.validate():
            form.bind(article)
            request.flash('Saved changes.', 'success')
            return HTTPFound(location=request.current_route_url())

        return dict(article=article, renderer=FormRenderer(form))

class ArticleListView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:articles', renderer='admin/articles.html',
                 permission='authenticated')
    def index(self):
        q = model.Session.query(model.Article)
        return dict(articles=q.all())


