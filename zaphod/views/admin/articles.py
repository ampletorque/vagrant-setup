from pyramid.view import view_defaults
from venusian import lift
from formencode import validators

from ... import model

from ...admin import (NodeListView, NodeEditView, NodeUpdateForm,
                      NodeCreateView, NodeDeleteView)


@view_defaults(route_name='admin:article', renderer='admin/article.html',
               permission='admin')
@lift()
class ArticleEditView(NodeEditView):
    cls = model.Article

    class UpdateForm(NodeUpdateForm):
        "Schema for validating article update form."
        category = validators.String(max=255)
        show_heading = validators.Bool()
        show_article_list = validators.Bool()


@view_defaults(route_name='admin:articles', renderer='admin/articles.html',
               permission='admin')
@lift()
class ArticleListView(NodeListView):
    cls = model.Article


@view_defaults(route_name='admin:articles:new',
               renderer='admin/articles_new.html', permission='admin')
@lift()
class ArticleCreateView(NodeCreateView):
    cls = model.Article
    obj_route_name = 'admin:article'


@view_defaults(route_name='admin:article:delete', permission='admin')
@lift()
class ArticleDeleteView(NodeDeleteView):
    cls = model.Article
    list_route_name = 'admin:articles'
