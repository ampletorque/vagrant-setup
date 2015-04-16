from lxml import etree, objectify

from pyramid.view import view_config
from pyramid.response import Response

from .. import model


class Sitemap(object):

    def __init__(self, **defaults):
        self.E = objectify.ElementMaker(
            annotate=False,
            namespace=u'http://www.sitemaps.org/schemas/sitemap/0.9',
            nsmap={None: u'http://www.sitemaps.org/schemas/sitemap/0.9'})
        self.defaults = defaults
        self.urls = []

    def add(self, loc, **params):
        params = dict(self.defaults, loc=loc, **params)
        self.urls.append(self.E.url(*[getattr(self.E, k)(v) for k, v in
                                      params.items()]))

    def render(self):
        urlset = self.E.urlset(*self.urls)
        return etree.tostring(
            urlset, encoding=u'utf8',
            xml_declaration=u'<?xml version="1.0" encoding="UTF-8"?>',
            pretty_print=True)


@view_config(route_name='sitemap')
class SitemapView(object):

    exclude = ()

    exclude_lastmod = (model.Tag, model.Creator)

    priorities = {model.Project: 0.9,
                  model.Article: 0.1,
                  None: 0.1}

    changefreqs = {model.Project: 'daily',
                   model.Article: 'monthly',
                   None: 'monthly'}

    def __init__(self, request):
        self.request = request

    def _handle_node(self, node):
        cls = node.__class__

        params = dict(
            priority=self.priorities.get(cls, self.priorities[None]),
            changefreq=self.changefreqs.get(cls, self.changefreqs[None]))

        if cls not in self.exclude_lastmod:
            params['lastmod'] = node.updated_time.strftime('%Y-%m-%d')

        return params

    def _query_nodes(self):
        q = model.Session.query(model.Node).\
            filter_by(published=True, listed=True)
        for node in q:
            if (isinstance(node, model.Project) and not node.is_live()):
                continue
            if isinstance(node, self.exclude):
                continue
            yield node

    def __call__(self):
        request = self.request
        sitemap = Sitemap()
        sitemap.add(request.route_url('index'), priority=1.0,
                    changefreq='daily')

        for node in self._query_nodes():
            params = self._handle_node(node)
            sitemap.add(request.node_url(node), **params)

        # Note that we need to call str() on the content-type here because WSGI
        # on Python 2 is expecting a str (not unicode) header value, but on
        # Python 3 will want a str (unicode) value.
        return Response(sitemap.render(), content_type=str('application/xml'))
