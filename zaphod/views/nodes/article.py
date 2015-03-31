from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from ... import model

from . import NodePredicate


@view_config(route_name='node', renderer='article.html',
             custom_predicates=[NodePredicate(model.Article)])
def article_view(context, request):
    article = context.node
    if article.show_article_list:
        related_articles = model.Session.query(model.Article).\
            filter_by(category=article.category).\
            filter(model.Article.id != article.id)
    else:
        related_articles = []

    return {
        'article': article,
        'related_articles': related_articles,
    }
