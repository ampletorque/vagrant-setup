from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ... import model


def article_view(article, system):
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
    config.add_node_view(article_view, model.Article, renderer='article.html')
