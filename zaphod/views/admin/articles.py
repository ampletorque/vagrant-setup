from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import validators

from ... import model

from ...admin import (NodeListView, NodeEditView, NodeUpdateForm,
                      NodeCreateView)


@view_defaults(route_name='admin:article', renderer='admin/article.html')
@lift()
class ArticleEditView(NodeEditView):
    cls = model.Article

    class UpdateForm(NodeUpdateForm):
        "Schema for validating article update form."
        category = validators.UnicodeString(max=255)
        show_heading = validators.Bool()
        show_article_list = validators.Bool()


@view_defaults(route_name='admin:articles', renderer='admin/articles.html')
@lift()
class ArticleListView(NodeListView):
    cls = model.Article


@view_defaults(route_name='admin:articles:new',
               renderer='admin/articles_new.html')
@lift()
class ArticleCreateView(NodeCreateView):
    cls = model.Article
    obj_route_name = 'admin:article'
