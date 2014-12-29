from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.renderers import render

from .. import model


def article_renderer(article, system):
    request = system['request']

    if article.show_article_list:
        related_articles = model.Session.query(model.Article).\
            filter_by(category=article.category).\
            filter(model.Article.id != article.id)
    else:
        related_articles = []

    return render('article.html', {
        'article': article,
        'related_articles': related_articles,
    }, request)


def includeme(config):
    config.add_node_renderer(article_renderer, model.Article)
