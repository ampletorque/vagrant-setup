from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ... import model

from . import NodePredicate


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


def includeme(config):
    config.add_view(article_view,
                    route_name='node',
                    custom_predicates=[NodePredicate(model.Article)],
                    renderer='article.html')
