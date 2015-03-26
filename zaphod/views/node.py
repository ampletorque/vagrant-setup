from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from six.moves.urllib.parse import quote

from pyramid.httpexceptions import HTTPNotFound, HTTPMovedPermanently
from pyramid.view import view_config
from pyramid.renderers import render
from sqlalchemy.orm.exc import NoResultFound

from .. import model
from ..nodes import lookup_node_view


class NodeView(object):

    def __init__(self, request):
        self.request = request

    def _query_match(self, path):
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

    @view_config(route_name='node', renderer='htmlstring')
    def view(self):
        request = self.request
        path = request.matchdict['path']
        alias, suffix = self._query_match(path)
        node = alias.node

        node_info = lookup_node_view(request.registry, node.__class__, suffix)

        if not node_info:
            raise HTTPNotFound

        if not alias.canonical:
            # Redirect to the canonical alias.
            canon_url = request.node_url(node, suffix, _query=request.params)
            raise HTTPMovedPermanently(location=canon_url)

        view, renderer = node_info

        system = dict(request=request)
        data = view(node, system)
        if renderer:
            return render(renderer, data, request)
        else:
            return data
