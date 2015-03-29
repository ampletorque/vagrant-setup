from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from six.moves.urllib.parse import quote

from pyramid.httpexceptions import HTTPNotFound, HTTPMovedPermanently
from sqlalchemy.orm.exc import NoResultFound

from ... import model


class NodePredicate(object):

    def __init__(self, cls, suffix=None):
        self.cls = cls
        self.suffix = suffix

    def query_match(self, path):
        """
        Given a list of path components (which would be /-delimited in the
        URL), attempt to find a node that matches the longest common subset of
        those path components. Then, return the node and the remaining path
        components (the 'suffix').
        """
        for suffix_chunks in range(len(path)):
            if suffix_chunks > 0:
                suffix = tuple(path[-suffix_chunks:])
                lookup_path = path[:-suffix_chunks]
            else:
                suffix = None
                lookup_path = path
            lookup_path = '/'.join(lookup_path)
            lookup_path = lookup_path.encode('utf8', 'replace')
            lookup_path = quote(lookup_path)
            try:
                alias = model.Session.query(model.Alias).\
                    filter_by(path=lookup_path).\
                    join(model.Alias.node).\
                    filter(model.Node.published == True).\
                    one()
            except NoResultFound:
                pass
            else:
                return alias, suffix
        raise HTTPNotFound

    def load_node(self, request):
        alias, suffix = self.query_match(request.matchdict['path'])
        node = alias.node

        if not alias.canonical:
            # Redirect to the canonical alias.
            raise HTTPMovedPermanently(
                location=request.node_url(node, suffix, _query=request.params))

        return node, suffix

    def __call__(self, context, request):
        if not hasattr(context, 'node'):
            context.node, context.suffix = self.load_node(request)
        return (isinstance(context.node, self.cls) and
                context.suffix == self.suffix)


def includeme(config):
    config.include('.article')
    config.include('.creator')
    config.include('.project')
    config.include('.update')
    config.include('.tag')
    config.include('.provider')
    config.include('.provider_type')
